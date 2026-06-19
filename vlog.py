import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import urllib.request
import tempfile
import numpy as np
import imageio
import cv2

# 1. 페이지 기본 설정
st.set_page_config(page_title="나만의 브이로그 메이커", layout="wide")
st.title("🎬 초간단 브이로그 제작 프로그램")
st.write("사진을 올리고, 자막과 음악을 넣어 나만의 스토리보드를 만들어보세요!")

# 프로그램 내부 저장소(세션 상태) 초기화
if "project_images" not in st.session_state:
    st.session_state.project_images = []

# -------------------------------------------------------------------------
# [함수] 인터넷에서 한글 폰트를 자동으로 다운로드하는 시스템
# -------------------------------------------------------------------------
@st.cache_resource
def load_stable_korean_font(size):
    font_filename = "NanumGothic.ttf"
    if not os.path.exists(font_filename):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, font_filename)
        except:
            pass

    if os.path.exists(font_filename):
        try:
            return ImageFont.truetype(font_filename, int(size))
        except:
            pass

    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc",
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, int(size))
            except:
                continue
    return ImageFont.load_default()

# -------------------------------------------------------------------------
# [함수] 자막 자동 줄바꿈 시스템 (20자 기준)
# -------------------------------------------------------------------------
def wrap_text(text, max_chars=20):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + word) <= max_chars:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    final_lines = []
    for line in lines:
        while len(line) > max_chars:
            final_lines.append(line[:max_chars])
            line = line[max_chars:]
        if line:
            final_lines.append(line)
    return "\n".join(final_lines)

# -------------------------------------------------------------------------
# [함수] 이미지에 자막 합성하기
# -------------------------------------------------------------------------
def draw_text_on_image(image, text, position, color, size):
    img_to_draw = image.copy()
    draw = ImageDraw.Draw(img_to_draw)
    width, height = img_to_draw.size
    
    font = load_stable_korean_font(size)
    wrapped_text = wrap_text(text, max_chars=20)
    lines = wrapped_text.split('\n')
    num_lines = len(lines)
    
    max_line_width = 0
    line_heights = []
    for line in lines:
        if font and hasattr(draw, "textbbox"):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            line_h = bbox[3] - bbox[1]
        else:
            line_w = len(line) * (size * 0.75)
            line_h = size
        if line_w > max_line_width:
            max_line_width = line_w
        line_heights.append(line_h)
        
    total_text_height = sum(line_heights) + (15 * (num_lines - 1))
    
    if position == "상단 (Top)":
        y = 60
    elif position == "중단 (Middle)":
        y = (height - total_text_height) // 2
    else:
        y = height - total_text_height - 80
        
    current_y = y
    for line in lines:
        if font and hasattr(draw, "textbbox"):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
        else:
            line_w = len(line) * (size * 0.75)
            
        line_x = (width - line_w) // 2
        
        # 글자 외곽선 효과
        outline_amount = max(1, int(size // 25)) 
        for adj_x in range(-outline_amount, outline_amount + 1):
            for adj_y in range(-outline_amount, outline_amount + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((line_x + adj_x, current_y + adj_y), line, fill="#000000", font=font)
        
        draw.text((line_x, current_y), line, fill=color, font=font)
        current_y += (size + 15) 
        
    return img_to_draw

# -------------------------------------------------------------------------
# 사이드바: 3단계 - 저작권 프리 배경음악 설정
# -------------------------------------------------------------------------
st.sidebar.header("🎵 3단계: 배경음악 선택")
bgm_list = {
    "선택 안함": "",
    "신나는 여행 느낌 (Happy Fast)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "잔잔한 일상 느낌 (Calm Daily)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "감성적인 저녁 느낌 (Emotional Night)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
}

selected_bgm = st.sidebar.selectbox("무료 BGM 리스트", list(bgm_list.keys()))
bgm_url = bgm_list[selected_bgm]

if bgm_url:
    st.sidebar.write("🎧 BGM 미리듣기:")
    st.sidebar.audio(bgm_url, format="audio/mp3")

# -------------------------------------------------------------------------
# 메인 화면: 1단계 - 사진 업로드 및 자막 편집
# -------------------------------------------------------------------------
st.header("📸 1단계: 사진 올리고 자막 넣기")
uploaded_files = st.file_uploader("브이로그에 사용할 사진들을 모두 선택해주세요.", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        if file.name not in [img.get("name") for img in st.session_state.project_images]:
            img = Image.open(file)
            st.session_state.project_images.append({
                "name": file.name,
                "original": img,
                "edited": img,
                "text": "지아랑 온유는 마라탕을 좋아해♥",
                "position": "상단 (Top)",
                "color": "#00FF00", 
                "size": 80
            })

if st.session_state.project_images:
    st.write("---")
    st.subheader("🖼️ 한 장 한 장 자막 완성하기")
    
    for i, item in enumerate(st.session_state.project_images):
        with st.expander(f"📷 {i+1}번 사진 편집: {item['name']}", expanded=False): # 가독성을 위해 기본 접힘 상태로 변경
            col1, col2 = st.columns([1, 1])
            
            with col1:
                txt = st.text_input(f"자막 타이핑", value=item["text"], key=f"txt_{i}")
                pos = st.selectbox("자막 위치", ["상단 (Top)", "중단 (Middle)", "하단 (Bottom)"], index=["상단 (Top)", "중단 (Middle)", "하단 (Bottom)"].index(item["position"]), key=f"pos_{i}")
                col_picker = st.color_picker("글자 색상 선택", value=item["color"], key=f"col_{i}")
                size_slider = st.slider("글자 크기", 20, 200, value=item["size"], key=f"size_{i}")
                
                if st.button(f"✨ {i+1}번 사진 자막 적용하기", key=f"btn_{i}"):
                    st.session_state.project_images[i]["text"] = txt
                    st.session_state.project_images[i]["position"] = pos
                    st.session_state.project_images[i]["color"] = col_picker
                    st.session_state.project_images[i]["size"] = size_slider
                    
                    edited_img = draw_text_on_image(item["original"], txt, pos, col_picker, size_slider)
                    st.session_state.project_images[i]["edited"] = edited_img
                    st.success("자막이 정상 반영되었습니다!")
                    st.rerun()
                
            with col2:
                st.image(st.session_state.project_images[i]["edited"], use_container_width=True)

# -------------------------------------------------------------------------
# 메인 화면: 2단계 - 순서 정하기 및 편집
# -------------------------------------------------------------------------
if st.session_state.project_images:
    st.write("---")
    st.header("🔀 2단계: 순서 정하기 및 관리")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("❌ 사진 제외하기")
        delete_target = st.selectbox("삭제할 사진 선택", ["선택 안함"] + [f"{idx+1}번: {img['name']}" for idx, img in enumerate(st.session_state.project_images)])
        if delete_target != "선택 안함":
            target_idx = int(delete_target.split("번")[0]) - 1
            if st.button("선택한 사진 최종 삭제"):
                st.session_state.project_images.pop(target_idx)
                st.rerun()

    with col_m2:
        st.subheader("🔄 순서 재배치")
        new_order = []
        for idx, item in enumerate(st.session_state.project_images):
            chosen_pos = st.number_input(f"'{item['name']}' ({idx+1}번) -> 이동할 위치:", min_value=1, max_value=len(st.session_state.project_images), value=idx+1, key=f"order_{idx}")
            new_order.append((chosen_pos, item))
            
        if st.button("순서 변경 적용하기"):
            new_order.sort(key=lambda x: x[0])
            st.session_state.project_images = [item[1] for item in new_order]
            st.success("순서가 변경되었습니다!")
            st.rerun()

    # -------------------------------------------------------------------------
    # 최종 확인 및 🎬 동영상 제작 엔진 (새로 추가된 핵심 로직)
    # -------------------------------------------------------------------------
    st.write("---")
    st.header("🎬 3단계: 최종 브이로그 동영상 렌더링 및 다운로드")
    st.write(f"🎵 현재 선택된 배경음악: **{selected_bgm}**")
    
    # 동영상 설정 옵션
    duration_per_image = st.slider("⏱️ 사진 1장당 노출 시간 (초)", 1, 10, value=3)
    
    if st.button("🚀 MP4 고화질 브이로그 영상 제작 시작", type="primary"):
        with st.spinner("🎬 자막 사진들과 음악을 융합하여 동영상을 만드는 중입니다... 잠시만 기다려주세요!"):
            try:
                frames = []
                temp_files = []
                fps = 24
                
                # 1. 자막이 적용된 이미지들을 프레임으로 변환
                for item in st.session_state.project_images:
                    tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    item["edited"].save(tmp_img.name)
                    temp_files.append(tmp_img.name)
                    
                    # 이미지를 numpy 배열로 로드
                    img = imageio.imread(tmp_img.name)
                    
                    # duration_per_image 초 동안 프레임 반복
                    frame_count = int(fps * duration_per_image)
                    for _ in range(frame_count):
                        frames.append(img)
                
                # 2. 최종 동영상 출력 임시 파일 생성
                output_video_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
                
                # imageio로 비디오 파일 저장 (FFMPEG backend 사용)
                writer = imageio.get_writer(output_video_path, fps=fps, codec='libx264')
                for frame in frames:
                    writer.append_data(frame)
                writer.close()
                
                # 5. 완성 파일 읽어와서 저장 및 다운로드 기능 활성화
                with open(output_video_path, "rb") as f:
                    video_bytes = f.read()
                
                st.success("🎉 성공적으로 브이로그 영상이 탄생했습니다! 아래에서 확인하고 다운로드하세요.")
                
                # 웹뷰 미리보기 플레이어
                st.video(video_bytes)
                
                # 최종 PC/모바일 저장 버튼
                st.download_button(
                    label="💾 내 컴퓨터/폰에 브이로그 동영상 저장하기",
                    data=video_bytes,
                    file_name="my_vlog.mp4",
                    mime="video/mp4"
                )
                
                # 사용된 임시 파일들 정리정돈
                for path in temp_files:
                    if os.path.exists(path):
                        os.remove(path)
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                    
            except Exception as e:
                st.error(f"동영상 제작 중 예기치 못한 에러가 발생했습니다: {e}")

    # 최종 스토리보드 스냅샷 리스트 표시
    st.write("---")
    st.subheader("🖼️ 현재 정렬된 최종 스토리보드 구성")
    final_cols = st.columns(len(st.session_state.project_images))
    for idx, item in enumerate(st.session_state.project_images):
        with final_cols[idx]:
            st.write(f"🎥 {idx+1}번 화면")
            st.image(item["edited"], use_container_width=True)