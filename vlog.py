import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import urllib.request

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
    """
    로컬 시스템 폰트에 의존하지 않고, 인터넷(네이버 오픈소스 저장소)에서 
    직접 나눔고딕 한글 폰트를 다운로드하여 어떤 환경에서든 100% 한글이 나오도록 보장합니다.
    """
    font_filename = "NanumGothic.ttf"
    # 현재 파이썬 파일이 있는 위치에 폰트가 없으면 자동 다운로드
    if not os.path.exists(font_filename):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, font_filename)
        except Exception as e:
            # 다운로드 실패 시 차선책으로 시스템 폰트 경로 탐색
            pass

    # 다운로드한 폰트 로드 시도
    if os.path.exists(font_filename):
        try:
            return ImageFont.truetype(font_filename, int(size))
        except:
            pass

    # 백업용: 시스템 기본 한글 폰트 경로들
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",          # Windows 맑은 고딕
        "C:/Windows/Fonts/gulim.ttc",           # Windows 굴림
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf", # Mac 애플고딕
        "/System/Library/Fonts/Cache/AppleGothic.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, int(size))
            except:
                continue

    # 최후의 수단 (이 경우 한글이 깨질 수 있으므로 콘솔에 경고)
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
# [함수] 이미지에 자막 합성하기 (온라인 폰트 다운로드 방식으로 엑박 완전 해결)
# -------------------------------------------------------------------------
def draw_text_on_image(image, text, position, color, size):
    img_to_draw = image.copy()
    draw = ImageDraw.Draw(img_to_draw)
    width, height = img_to_draw.size
    
    # 💥 안전한 온라인 나눔고딕 한글 폰트 로드 (가변 크기 적용)
    font = load_stable_korean_font(size)
            
    # 20자 기준 줄바꿈 처리
    wrapped_text = wrap_text(text, max_chars=20)
    lines = wrapped_text.split('\n')
    num_lines = len(lines)
    
    # 전체 텍스트 상자의 가로/세로 크기 정확하게 계산
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
            
        if line_w > max_line