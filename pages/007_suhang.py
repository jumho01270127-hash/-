import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="방문객 분석", layout="wide")

# ----------------------------------
# 1. CSV 불러오기
# ----------------------------------
def load_csv():
    try:
        # UTF-8로 읽기
        df = pd.read_csv("tour.csv", encoding="utf-8")
    except:
        # 인코딩 에러 시 엔진 변경
        df = pd.read_csv("tour.csv", encoding="utf-8", engine="python", on_bad_lines="skip")

    # 컬럼 정리 (공백 제거 + BOM 제거)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace('\ufeff', '', regex=False)

    return df


df = load_csv()

# ----------------------------------
# 2. 데이터 구조 설정
# ----------------------------------

# 국가 컬럼 자동 추출
ignore_cols = ['해당연월', '관련부서', '데이터기준일자']
available_countries = [col for col in df.columns if col not in ignore_cols]

# 기본 선택 국가 (존재하는 경우만)
default_countries = [c for c in ["일본", "중국", "미국"] if c in available_countries]

# 월 리스트 생성
available_months = df['해당연월'].unique().tolist()
available_months.sort()

# ----------------------------------
# 3. 사이드바 UI (국가/월 선택)
# ----------------------------------
st.sidebar.header("🔍 필터 선택")

selected_countries = st.sidebar.multiselect(
    "국가 선택 (그래프)",
    options=available_countries,
    default=default_countries
)

selected_month = st.sidebar.selectbox(
    "월 선택",
    available_months
)

# ----------------------------------
# 4. 데이터 필터링
# ----------------------------------
filtered = df[df['해당연월'] == selected_month]

# 선택한 국가들만 추출한 데이터프레임 변환
plot_df = filtered[['해당연월'] + selected_countries].melt(
    id_vars='해당연월',
    var_name='국가',
    value_name='방문자수'
)

# ----------------------------------
# 5. Plotly 그래프
# ----------------------------------
if len(selected_countries) == 0:
    st.warning("국가를 1개 이상 선택하세요.")
else:
    fig = px.bar(
        plot_df,
        x="국가",
        y="방문자수",
        color="국가",
        title=f"🌏 {selected_month} 월 국가별 방문자 수"
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------
# 6. 데이터 테이블 보기
# ----------------------------------
with st.expander("📄 원본 데이터 보기"):
    st.dataframe(df)
