"""
파일 위치: pages/school_dashboard.py  (Streamlit Cloud에서 app 폴더 루트에 `pages/` 폴더로 넣으세요)
CSV 파일: 루트 폴더에 `제주특별자치도교육청_학교현황_20251102.csv` 를 넣으세요.

requirements.txt (아래 내용을 별도 파일로 저장하거나 Streamlit Cloud의 requirements.txt에 붙여넣으세요):

# ---------- requirements.txt START ----------
streamlit
pandas
plotly
openpyxl
pytz
# ---------- requirements.txt END ------------

설명:
- 설립구분(공립/사립)을 색상으로 구분합니다. 요청대로 공립은 흰색, 사립은 파랑색(기본 파란색 계열)입니다.
- 자치구별 분포(막대차트)와 학교급별 통계, 필터링 가능한 테이블을 제공합니다.
- CSV가 cp949(또는 utf-8)가 혼재되어 있을 수 있어 기본적으로 cp949로 읽고 실패하면 utf-8로 재시도합니다.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="제주 교육청 학교현황 대시보드", layout="wide")

# ------------------ helper: load data ------------------
@st.cache_data
def load_csv(path: str):
    # try cp949 first, then utf-8
    try:
        df = pd.read_csv(path, encoding='cp949')
    except Exception:
        df = pd.read_csv(path, encoding='utf-8')
    return df

CSV_PATH = "제주특별자치도교육청_학교현황_20251102.csv"

st.title("제주특별자치도교육청 — 학교현황 대시보드")

try:
    df = load_csv(CSV_PATH)
except FileNotFoundError:
    st.error(f"CSV 파일을 찾을 수 없습니다: `{CSV_PATH}`\n루트 폴더에 파일을 업로드했는지 확인하세요.")
    st.stop()

# 기본 전처리
# 통일된 컬럼명(예상 컬럼이름이 한글이므로 소폭 정리)
expected_cols = ['학교급','설립구분','학교','자치구','남녀공학구분','개교일자','우편번호','주소','전화번호','팩스번호','홈페이지']
# 만약 컬럼이 다르면 가능한 공통 열만 사용
cols_present = [c for c in expected_cols if c in df.columns]
if len(cols_present) < 4:
    st.warning("CSV에 예상 컬럼이 없습니다. 현재 컬럼: " + ", ".join(df.columns.tolist()))

# 날짜형 변환 시도
if '개교일자' in df.columns:
    try:
        df['개교일자'] = pd.to_datetime(df['개교일자'], errors='coerce')
    except Exception:
        pass

# 사용자 인터페이스: 필터
with st.sidebar:
    st.header("필터")
    school_levels = ['전체'] + sorted(df['학교급'].dropna().unique().tolist()) if '학교급' in df.columns else ['전체']
    sel_level = st.selectbox("학교급", school_levels)

    districts = ['전체'] + sorted(df['자치구'].dropna().unique().tolist()) if '자치구' in df.columns else ['전체']
    sel_district = st.selectbox("자치구", districts)

    types = ['전체'] + sorted(df['설립구분'].dropna().unique().tolist()) if '설립구분' in df.columns else ['전체']
    sel_type = st.selectbox("설립구분", types)

    show_table = st.checkbox("원본 테이블 보기", value=True)

# 필터 적용
df_filtered = df.copy()
if sel_level != '전체':
    df_filtered = df_filtered[df_filtered['학교급'] == sel_level]
if sel_district != '전체':
    df_filtered = df_filtered[df_filtered['자치구'] == sel_district]
if sel_type != '전체':
    df_filtered = df_filtered[df_filtered['설립구분'] == sel_type]

# ---------- 요약 KPI ----------
col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    st.metric("전체 학교 수", len(df))
with col2:
    st.metric("현재 선택된 학교 수", len(df_filtered))
with col3:
    if '자치구' in df.columns:
        st.metric("자치구 수", df['자치구'].nunique())
    else:
        st.metric("자치구 수", "N/A")
with col4:
    if '설립구분' in df.columns:
        st.metric("설립구분 유형 수", df['설립구분'].nunique())
    else:
        st.metric("설립구분 유형 수", "N/A")

st.markdown("---")

# ------------ Plotly 시각화 -------------
# 색맵: 공립=흰색, 사립=파랑
color_map = {
    '공립': '#FFFFFF',  # 흰색
    '사립': '#0074D9',  # 파란색 계열
}
# 만약 다른 값이 있으면 자동으로 색 지정
unique_types = df['설립구분'].dropna().unique().tolist() if '설립구분' in df.columns else []
for t in unique_types:
    if t not in color_map:
        color_map[t] = None  # plotly가 자동으로 색 지정

# 1) 자치구별 & 설립구분별 분포 (그룹화된 막대)
if '자치구' in df.columns and '설립구분' in df.columns:
    grouped = df.groupby(['자치구','설립구분']).size().reset_index(name='count')
    fig_district = px.bar(grouped, x='자치구', y='count', color='설립구분', barmode='group',
                          color_discrete_map=color_map,
                          labels={'count':'학교 수','자치구':'자치구','설립구분':'설립구분'})
    # 흰색 바 대비선 보이도록 라인
    fig_district.update_traces(marker_line_color='black', marker_line_width=1)
    fig_district.update_layout(title='자치구별 설립구분 분포', xaxis_title='자치구', yaxis_title='학교 수', legend_title='설립구분')
    st.plotly_chart(fig_district, use_container_width=True)

# 2) 학교급별 통계 (스택/그룹 선택 가능)
if '학교급' in df.columns and '설립구분' in df.columns:
    st.subheader('학교급별 분포')
    mode = st.radio('표시 방식', ['그룹', '스택'], index=0)
    bmode = 'group' if mode == '그룹' else 'relative'
    grouped2 = df.groupby(['학교급','설립구분']).size().reset_index(name='count')
    fig_level = px.bar(grouped2, x='학교급', y='count', color='설립구분', barmode=bmode, color_discrete_map=color_map,
                       labels={'count':'학교 수','학교급':'학교급'})
    fig_level.update_traces(marker_line_color='black', marker_line_width=1)
    fig_level.update_layout(title='학교급별 설립구분 분포', xaxis_title='학교급', yaxis_title='학교 수', legend_title='설립구분')
    st.plotly_chart(fig_level, use_container_width=True)

# 3) 개교 연도 분포 (가능하면)
if '개교일자' in df.columns and pd.api.types.is_datetime64_any_dtype(df['개교일자']):
    st.subheader('개교 연도별 분포')
    df['개교연도'] = df['개교일자'].dt.year
    year_counts = df.groupby(['개교연도','설립구분']).size().reset_index(name='count')
    fig_year = px.bar(year_counts, x='개교연도', y='count', color='설립구분', color_discrete_map=color_map,
                      labels={'count':'학교 수','개교연도':'연도'})
    fig_year.update_traces(marker_line_color='black', marker_line_width=0.5)
    fig_year.update_layout(xaxis={'type':'category'}, title='개교 연도별 학교 수')
    st.plotly_chart(fig_year, use_container_width=True)

st.markdown("---")

# --------------- 테이블 및 다운로드 ---------------
if show_table:
    st.subheader('원본 데이터 (필터 적용됨)')
    st.dataframe(df_filtered.reset_index(drop=True))
    # 다운로드 버튼: 필터된 데이터
    csv_buffer = StringIO()
    df_filtered.to_csv(csv_buffer, index=False)
    st.download_button(label="필터된 데이터 다운로드 (CSV)", data=csv_buffer.getvalue(), file_name="filtered_schools.csv", mime='text/csv')

# --------------- requirements 다운로드 ---------------
requirements_text = """streamlit
pandas
plotly
openpyxl
pytz
"""

st.sidebar.download_button("requirements.txt 다운로드", data=requirements_text, file_name="requirements.txt")

st.info("CSV 파일 이름: `제주특별자치도교육청_학교현황_20251102.csv`. 이 파일을 Streamlit Cloud(앱 루트)에 업로드 한 뒤 이 페이지를 복사해서 pages/ 아래에 넣으세요.")

# 끝

