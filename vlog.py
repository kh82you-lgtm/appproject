import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

# 1. 페이지 기본 설정
st.set_page_config(page_title="나만의 브이로그 메이커", layout="wide")
st.title("🎬 초간단 브이로그 제작 프로그램")
st.write("사진을 올리고, 자막과 음악을 넣어 나만의 스토리보드를 만들어보세요!")

# 프로그램 내부 저장소(세션 상태) 초기화
if "project_images" not in st.session_state:
    st.session_state.project_images = []

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
# [함수] 이미지에 자막 합성하기 (한글 깨짐 해결 및 글자 테두리 효과)
# -------------------------------------------------------------------------
def draw_text_on_image(image, text, position, color, size):
    img_to_draw = image.copy()
    draw = ImageDraw.Draw(img_to_draw)
    width, height = img_to_draw.size
    
    # 💥 [핵심] 확실하게 100% 한글이 지원되는 시스템 폰트만 엄선하여 탐색
    font = None
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",          # 윈도우 맑은 고딕 (가장 확실)
        "C:/Windows/Fonts/gulim.ttc",           # 윈도우 굴림
        "C:/Windows/Fonts/batang.ttc",          # 윈도우 바탕
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf", # 맥 애플고딕
        "/System/Library/Fonts/Cache/AppleGothic.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf" # 맥 유니코드
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, int(size))
                break
            except:
                continue
                
    # 만약 위의 절대 경로에서 실패할 경우 시스템 환경 변수에서 맑은고딕 자동 검색
    if font is None:
        try:
            font = ImageFont.truetype("malgun.ttf", int(size))
        except:
            try:
                font = ImageFont.truetype("gulim.ttc", int(size))
            except:
                # 최후의 보루: Pillow 최신 버전 가변 기본 폰트
                try:
                    font = ImageFont.load_default(size=int(size))
                except:
                    font = ImageFont.load_default()
            
    # 20자 기준 줄바꿈 처리
    wrapped_text = wrap_text(text, max_chars=20)
    lines = wrapped_text.split('\n')
    num_lines = len(lines)
    
    # 전체 텍스트 상자의 대략적인 가로/세로 크기 계산
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
    
    # 1. 세로(Y축) 시작 위치 결정
    if position == "상단 (Top)":
        y = 60
    elif position == "중단 (Middle)":
        y = (height - total_text_height) // 2
    else:
        y = height - total_text_height - 80
        
    # 2. 회색 박스 배경을 없애고, 글자 자체만 중앙 정렬하여 그리기
    current_y = y
    for line in lines:
        if font and hasattr(draw, "textbbox"):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
        else:
            line_w = len(line) * (size * 0.75)
            
        line_x = (width - line_w) // 2
        
        # ⭐ [가독성 강화] 어떤 배경 사진에서도 글씨가 잘 보이도록 검은색 테두리(외곽선) 넣기
        # 글씨 주위 8방향에 얇게 검은색 글씨를 먼저 적어 테두리 효과를 만듭니다.
        outline_amount = max(1, int(size // 25)) # 글자 크기에 비례하는 영리한 테두리 두께
        for adj_x in range(-outline_amount, outline_amount + 1):
            for adj_y in range(-outline_amount, outline_amount + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((line_x + adj_x, current_y + adj_y), line, fill="#000000", font=font)
        
        # 테두리 위에 사용자가 선택한 본래 색상(초록색 등)의 글자를 얹어줍니다.
        draw.text((line_x, current_y), line, fill=color, font=font)
        current_y += (size + 15) # 줄 간격 격차
        
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

if bgm_list[selected_bgm]:
    st.sidebar.write("🎧 BGM 미리듣기:")
    st.sidebar.audio(bgm_list[selected_bgm], format="audio/mp3")

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
                "color": "#00FF00", # 사용자가 좋아하시는 예쁜 형광 초록색
                "size": 80
            })

# 업로드된 사진 편집 창 표시
if st.session_state.project_images:
    st.write("---")
    st.subheader("🖼️ 한 장 한 장 자막 완성하기")
    
    for i, item in enumerate(st.session_state.project_images):
        with st.expander(f"📷 {i+1}번 사진 편집: {item['name']}", expanded=True):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                txt = st.text_input(f"자막 타이핑 (최대 20자 제안)", value=item["text"], key=f"txt_{i}")
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
                    st.success("한글 자막이 완벽하게 반영되었습니다!")
                    st.rerun()
                
            with col2:
                st.write("🔍 미리보기 (좌우 센터 정렬 및 글자 외곽선 효과 적용)")
                st.image(st.session_state.project_images[i]["edited"], use_container_width=True)

# -------------------------------------------------------------------------
# 메인 화면: 2단계 - 순서 정하기 및 편집(추가/삭제)
# -------------------------------------------------------------------------
if st.session_state.project_images:
    st.write("---")
    st.header("🔀 2단계: 순서 정하기 및 관리")
    
    st.subheader("❌ 사진 제외하기")
    delete_target = st.selectbox("삭제할 사진을 선택하세요", ["선택 안함"] + [f"{idx+1}번: {img['name']}" for idx, img in enumerate(st.session_state.project_images)])
    if delete_target != "선택 안함":
        target_idx = int(delete_target.split("번")[0]) - 1
        if st.button("선택한 사진 최종 삭제"):
            st.session_state.project_images.pop(target_idx)
            st.rerun()

    st.subheader("🔄 순서 재배치")
    new_order = []
    for idx, item in enumerate(st.session_state.project_images):
        chosen_pos = st.number_input(f"'{item['name']}'의 현재 위치: {idx+1} -> 이동할 위치:", min_value=1, max_value=len(st.session_state.project_images), value=idx+1, key=f"order_{idx}")
        new_order.append((chosen_pos, item))
        
    if st.button("순서 변경 적용하기"):
        new_order.sort(key=lambda x: x[0])
        st.session_state.project_images = [item[1] for item in new_order]
        st.success("순서가 성공적으로 변경되었습니다!")
        st.rerun()

    # -------------------------------------------------------------------------
    # 최종 확인 존
    # -------------------------------------------------------------------------
    st.write("---")
    st.header("🎬 최종 브이로그 스토리보드 확인")
    st.write(f"🎵 적용된 BGM: **{selected_bgm}**")
    
    final_cols = st.columns(len(st.session_state.project_images))
    for idx, item in enumerate(st.session_state.project_images):
        with final_cols[idx]:
            st.write(f"🎥 {idx+1}번 화면")
            st.image(item["edited"], use_container_width=True)