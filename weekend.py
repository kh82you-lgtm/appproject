

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정 (로컬 환경 및 리눅스 서버 대응)
# 스트림릿 클라우드 배포 시 한글 깨짐을 방지하기 위해 기본 폰트나 나눔 폰트 설정을 권장합니다.
plt.rcParams['font.family'] = 'Malgun Gothic' # Windows용 (Mac은 AppleGothic)
plt.rcParams['axes.unicode_minus'] = False

# 1. 페이지 설정
st.set_page_config(page_title="주말/평일 대여점 이용량 분석", layout="wide")

st.title("📊 주말 vs 평일 대여점 이용량 대시보드")
st.markdown("업로드된 데이터를 기반으로 주말과 평일의 대여 현황을 비교합니다.")

# 2. 데이터 로드
@st.cache_data
def load_data():
    # 데이터 불러오기
    df = pd.read_csv("주말인기대여점_50.csv")
    # 인덱스를 대여점 번호(순위) 형태로 변환
    df.index = df.index + 1
    df.index.name = '대여점 순위'
    return df

try:
    df = load_data()

    # 3. 상단 주요 지표 (Metrics)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 데이터 수 (대여점 수)", f"{len(df)} 개")
    with col2:
        st.metric("주말 총 대여량", f"{df['주말'].sum():,}")
    with col3:
        st.metric("평일 총 대여량", f"{df['평일'].sum():,}")

    st.divider()

    # 4. 그래프 및 데이터 테이블 배치
    chart_col, data_col = st.columns([2, 1])

    with chart_col:
        st.subheader("📈 주말 및 평일 이용량 비교 차트")
        
        # 스트림릿 내장 라인 차트 사용 (깔끔하고 인터랙티브함)
        st.line_chart(df[['주말', '평일']])
        
        # 분포 비교를 위한 Boxplot (Matplotlib/Seaborn)
        st.subheader("📦 데이터 분포 비교 (Boxplot)")
        fig, ax = plt.subplots(figsize=(6, 3.5))
        sns.boxplot(data=df[['주말', '평일']], ax=ax, palette="Set2")
        ax.set_ylabel("대여량")
        st.pyplot(fig)

    with data_col:
        st.subheader("📑 대여점별 상세 데이터")
        # 검색 및 필터 기능 간단히 포함된 데이터프레임 출력
        st.dataframe(df, use_container_width=True, height=500)

except Exception as e:
    st.error(f"데이터를 읽어오는 중 오류가 발생했습니다: {e}")