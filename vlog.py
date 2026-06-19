import streamlit as st
from PIL import Image, ImageDraw, ImageFont

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
# [함수] 이미지에 자막 합성하기 (좌우 자동 중앙 정렬 기능 탑재)
# -------------------------------------------------------------------------
def draw_text_on_image(image, text, position, color, size):
    img_to_draw = image.copy()
    draw = ImageDraw.Draw(img_to_draw)
    width, height = img_to_draw.size
    
    # 20자 기준 자동 줄바꿈 처리
    wrapped_text = wrap_text(text, max_chars=20)
    
    # 시스템 기본 한글 폰트 불러오기
    font = None
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",       # Windows (맑은고딕)
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf", # Mac
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"     # Linux
    ]
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, int(size))
            break
        except:
            continue
            
    if font is None:
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
    # 줄바꿈된 텍스트 전체의 높이와 너비 계산
    lines = wrapped_text.split('\n')
    num_lines = len(lines)
    
    # 폰트 객체가 있을 때와 없을 때의 텍스트 크기 측정 방식 대응
    if font and hasattr(draw, "textbbox"):
        # 가장 긴 줄을 기준으로 가로 너비 측정
        max_line_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            if line_w > max_line_width:
                max_line_width = line_w
        
        # 전체 텍스트 높이 측정
        sample_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_height = sample_bbox[3] - sample_bbox[1]
    else:
        # 기본 폰트일 경우 대략적인 픽셀 계산 계산
        max_line_width = max([len(line) for line in lines]) * (size * 0.6)
        text_height = num_lines * (size + 5)
    
    # 1. 세로(Y축) 위치 설정
    if position == "상단 (Top)":
        y = 50
    elif position == "중단 (Middle)":
        y = (height - text_height) // 2
    else:
        y = height - text_height - 50
        
    # 2. 가로(X축) 자동 중앙 정렬 계산 
    # (이미지 전체 너비 - 글자 전체 너비) 나누기 2 = 정확한 중앙
    x = (width - max_line_width) // 2
    if x < 10:  # 글자가 사진보다 커서 밖으로 나가는 것 방지 최소 마진
        x = 10

    # 줄 단위로 개별 정렬하여 그려주기 (여러 줄일 때도 각각 중앙에 오도록)
    current_y = y
    for line in lines:
        if font and hasattr(draw, "textbbox"):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
        else:
            line_w = len(line) * (size * 0.6)
            
        line_x = (width - line_w) // 2
        draw.text((line_x, current_y), line, fill=color, font=font)
        current_y += (size + 10) # 다음 줄 간격
        
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
                "text": "지아랑 온유는 올리브영을 좋아해♥",
                "position": "상단 (Top)",
                "color": "#00FF00",
                "size": 60  # 센터 정렬 확인용으로 조금 키웠습니다
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
                size_slider = st.slider("글자 크기", 10, 150, value=item["size"], key=f"size_{i}")
                
                if st.button(f"✨ {i+1}번 사진 자막 적용하기", key=f"btn_{i}"):
                    st.session_state.project_images[i]["text"] = txt
                    st.session_state.project_images[i]["position"] = pos
                    st.session_state.project_images[i]["color"] = col_picker
                    st.session_state.project_images[i]["size"] = size_slider
                    
                    edited_img = draw_text_on_image(item["original"], txt, pos, col_picker, size_slider)
                    st.session_state.project_images[i]["edited"] = edited_img
                    st.success("중앙 정렬 자막이 정상적으로 반영되었습니다!")
                    st.rerun()
                
            with col2:
                st.write("🔍 미리보기 (좌우 자동 중앙 정렬 적용됨)")
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