"""
파일 위치: pages/school_dashboard.py  (Streamlit Cloud에서 app 루트에 `pages/` 폴더로 넣으세요)
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
- 오류 발생 시 더 친절한 에러 메시지와 파일 업로드 대체 경로를 추가했습니다.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
from pathlib import Path
import plotly.colors as plc

st.set_page_config(page_title="제주 교육청 학교현황 대시보드", layout="wide")

# ------------------ helper: load data ------------------
@st.cache_data
def try_read_csv(path: str):
    # 시도할 인코딩 목록
    encodings = ['cp949', 'euc-kr', 'utf-8', 'utf-8-sig']
    last_exc = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            return df
        except Exception as e:
            last_exc = e
    # 모두 실패하면 마지막 예외를 raise
    raise last_exc

CSV_PATH = Path(__file__).parents[1] / "제주특별자치도교육청_학교현황_20251102.csv"

st.title("제주특별자치도교육청 — 학교현황 대시보드")

# 파일 로드: 루트에 없으면 업로더로 대체
if CSV_PATH.exists():
    try:
        df = try_read_csv(str(CSV_PATH))
    except Exception as e:
        st.error(f"CSV를 읽는 중 오류가 발생했습니다: {e}")
        st.stop()
else:
    st.warning(f"루트에 CSV 파일이 없습니다: {CSV_PATH}
아래에서 파일을 업로드하세요.")
    uploaded = st.file_uploader("CSV 파일 업로드", type=['csv'])
    if uploaded is None:
        st.info("CSV 파일을 업로드 하거나 앱 루트에 파일을 놓으세요.")
        st.stop()
    try:
        df = pd.read_csv(uploaded, encoding='utf-8')
    except Exception:
        uploaded.seek(0)
        df = pd.read_csv(uploaded, encoding='cp949')

# 기본 전처리
expected_cols = ['학교급','설립구분','학교','자치구','남녀공학구분','개교일자','우편번호','주소','전화번호','팩스번호','홈페이지']
cols_present = [c for c in expected_cols if c in df.columns]
if len(cols_present) < 4:
    st.warning("CSV에 예상 컬럼이 없습니다. 현재 컬럼: " + ", ".join(df.columns.tolist()))

# 개교일자 -> datetime
if '개교일자' in df.columns:
    df['개교일자'] = pd.to_datetime(df['개교일자'], errors='coerce')

# 사이드바 필터
with st.sidebar:
    st.header("필터")
    school_levels = ['전체'] + (sorted(df['학교급'].dropna().unique().tolist()) if '학교급' in df.columns else [])
    sel_level = st.selectbox("학교급", school_levels)

    districts = ['전체'] + (sorted(df['자치구'].dropna().unique().tolist()) if '자치구' in df.columns else [])
    sel_district = st.selectbox("자치구", districts)

    types = ['전체'] + (sorted(df['설립구분'].dropna().unique().tolist()) if '설립구분' in df.columns else [])
    sel_type = st.selectbox("설립구분", types)

    show_table = st.checkbox("원본 테이블 보기", value=True)

# 필터 적용
df_filtered = df.copy()
if sel_level != '전체' and '학교급' in df.columns:
    df_filtered = df_filtered[df_filtered['학교급'] == sel_level]
if sel_district != '전체' and '자치구' in df.columns:
    df_filtered = df_filtered[df_filtered['자치구'] == sel_district]
if sel_type != '전체' and '설립구분' in df.columns:
    df_filtered = df_filtered[df_filtered['설립구분'] == sel_type]

# KPI
col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    st.metric("전체 학교 수", len(df))
with col2:
    st.metric("현재 선택된 학교 수", len(df_filtered))
with col3:
    st.metric("자치구 수", df['자치구'].nunique() if '자치구' in df.columns else 'N/A')
with col4:
    st.metric("설립구분 유형 수", df['설립구분'].nunique() if '설립구분' in df.columns else 'N/A')

st.markdown("---")

# 색맵 구성: 공립=흰색, 사립=파랑, 나머지는 Plotly 팔레트
unique_types = df['설립구분'].dropna().unique().tolist() if '설립구분' in df.columns else []
palette = plc.qualitative.Plotly
color_map = {}
other_idx = 0
for t in unique_types:
    if str(t).strip() == '공립':
        color_map[t] = '#FFFFFF'
    elif str(t).strip() == '사립':
        color_map[t] = '#1f77b4'
    else:
        color_map[t] = palette[other_idx % len(palette)]
        other_idx += 1

# 자치구별 설립구분 분포
if '자치구' in df.columns and '설립구분' in df.columns:
    grouped = df.groupby(['자치구','설립구분']).size().reset_index(name='count')
    fig_district = px.bar(grouped, x='자치구', y='count', color='설립구분', barmode='group',
                          color_discrete_map=color_map,
                          labels={'count':'학교 수','자치구':'자치구','설립구분':'설립구분'})
    # 공립(흰색) 바가 보이지 않는 문제 대응: 모든 trace에 테두리와 패턴 적용
    for i, trace in enumerate(fig_district.data):
        trace.marker.line.color = 'black'
        trace.marker.line.width = 0.8
        if trace.name in color_map and color_map[trace.name] == '#FFFFFF':
            # 흰색 바는 패턴을 넣어 가시성 확보
            trace.marker.pattern.shape = "/"
            trace.marker.opacity = 0.9
    fig_district.update_layout(title='자치구별 설립구분 분포', xaxis_title='자치구', yaxis_title='학교 수', legend_title='설립구분')
    st.plotly_chart(fig_district, use_container_width=True)

# 학교급별 분포
if '학교급' in df.columns and '설립구분' in df.columns:
    st.subheader('학교급별 분포')
    mode = st.radio('표시 방식', ['그룹', '스택'], index=0)
    bmode = 'group' if mode == '그룹' else 'relative'
    grouped2 = df.groupby(['학교급','설립구분']).size().reset_index(name='count')
    fig_level = px.bar(grouped2, x='학교급', y='count', color='설립구분', barmode=bmode, color_discrete_map=color_map,
                       labels={'count':'학교 수','학교급':'학교급'})
    for trace in fig_level.data:
        trace.marker.line.color = 'black'
        trace.marker.line.width = 0.8
        if trace.name in color_map and color_map[trace.name] == '#FFFFFF':
            trace.marker.pattern.shape = "x"
            trace.marker.opacity = 0.9
    fig_level.update_layout(title='학교급별 설립구분 분포', xaxis_title='학교급', yaxis_title='학교 수', legend_title='설립구분')
    st.plotly_chart(fig_level, use_container_width=True)

# 개교 연도 분포
if '개교일자' in df.columns and pd.api.types.is_datetime64_any_dtype(df['개교일자']):
    st.subheader('개교 연도별 분포')
    df['개교연도'] = df['개교일자'].dt.year
    year_counts = df.groupby(['개교연도','설립구분']).size().reset_index(name='count')
    fig_year = px.bar(year_counts, x='개교연도', y='count', color='설립구분', color_discrete_map=color_map,
                      labels={'count':'학교 수','개교연도':'연도'})
    for trace in fig_year.data:
        trace.marker.line.color = 'black'
        trace.marker.line.width = 0.5
        if trace.name in color_map and color_map[trace.name] == '#FFFFFF':
            trace.marker.pattern.shape = "."
            trace.marker.opacity = 0.9
    fig_year.update_layout(xaxis={'type':'category'}, title='개교 연도별 학교 수')
    st.plotly_chart(fig_year, use_container_width=True)

st.markdown("---")

# 테이블 및 다운로드
if show_table:
    st.subheader('원본 데이터 (필터 적용됨)')
    st.dataframe(df_filtered.reset_index(drop=True))
    csv_buffer = StringIO()
    df_filtered.to_csv(csv_buffer, index=False)
    st.download_button(label="필터된 데이터 다운로드 (CSV)", data=csv_buffer.getvalue(), file_name="filtered_schools.csv", mime='text/csv')

# requirements 다운로드
requirements_text = """streamlit
pandas
plotly
openpyxl
pytz
"""
st.sidebar.download_button("requirements.txt 다운로드", data=requirements_text, file_name="requirements.txt")

st.info("CSV 파일 이름: `제주특별자치도교육청_학교현황_20251102.csv`. 이 파일을 Streamlit Cloud(앱 루트)에 업로드 한 뒤 이 페이지를 복사해서 pages/ 아래에 넣으세요.")

# 끝
