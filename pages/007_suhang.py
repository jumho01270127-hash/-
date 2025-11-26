import os
import streamlit as st
import pandas as pd

# --- 현재 파일 기준 절대 경로 설정 ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # pages/
ROOT_DIR = os.path.dirname(CURRENT_DIR)                   # 루트
CSV_PATH = os.path.join(ROOT_DIR, "tour.csv")

st.sidebar.write(f"CSV 검사 경로: {CSV_PATH}")

# --- UTF-8로 읽기 ---
try:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    st.sidebar.success("데이터 로드 성공 (UTF-8)")
except Exception as e:
    st.error(f"CSV를 읽는 중 오류 발생: {e}")
    st.stop()



# --- 전처리 ---
df.columns = df.columns.str.strip()

try:
    df['해당연월'] = pd.to_datetime(df['해당연월'].astype(str), format="%Y-%m")
except Exception:
    df['해당연월'] = pd.to_datetime(df['해당연월'].astype(str), errors='coerce')

# 국가 컬럼 자동 탐색
num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
countries = [c for c in num_cols if c.lower() not in ('index',)]

df_long = df.melt(
    id_vars=['해당연월', '관련부서', '데이터기준일자'],
    value_vars=countries,
    var_name='국가',
    value_name='방문객수'
)

# 계절 함수
def month_to_season(m):
    if m in [12, 1, 2]:
        return "겨울"
    if m in [3, 4, 5]:
        return "봄"
    if m in [6, 7, 8]:
        return "여름"
    return "가을"

df_long['월'] = df_long['해당연월'].dt.month
df_long['연도'] = df_long['해당연월'].dt.year
df_long['시즌'] = df_long['월'].apply(month_to_season)

# --- 사이드바 ---
st.sidebar.header("필터 및 옵션")

year_options = sorted(df_long['연도'].unique())
selected_year = st.sidebar.selectbox("연도 선택", year_options, index=0)

month_options = ["전체"] + [f"{m:02d}" for m in sorted(df_long['월'].unique())]
selected_month = st.sidebar.selectbox("월 선택", month_options, index=0)

st.sidebar.markdown("### 시즌 선택")
col1, col2, col3, col4 = st.sidebar.columns(4)
season_selected = None
if col1.button("봄"): season_selected = "봄"
if col2.button("여름"): season_selected = "여름"
if col3.button("가을"): season_selected = "가을"
if col4.button("겨울"): season_selected = "겨울"

show_month = st.sidebar.button("선택한 월 보기")

default_countries = ["중국", "일본", "대만", "홍콩"]
# 옵션 목록
available_countries = df['국가'].unique().tolist()

# 기본 선택 국가들
default_countries = ["일본", "미국", "중국"]

# 옵션에 없는 값은 자동으로 제거
default_countries = [c for c in default_countries if c in available_countries]

selected_countries = st.sidebar.multiselect(
    "국가 선택 (그래프)",
    available_countries,        # 옵션 목록
    default=default_countries   # 안전하게 필터링된 기본값
)


# --- 필터 적용 ---
df_disp = df_long[df_long['연도'] == selected_year].copy()

if season_selected:
    df_disp = df_disp[df_disp['시즌'] == season_selected]

if selected_month != "전체" and show_month:
    df_disp = df_disp[df_disp['월'] == int(selected_month)]

# --- 상단 요약 카드 ---
total_visitors = int(df_disp['방문객수'].sum())
unique_countries = df_disp['국가'].nunique()
max_country = df_disp.groupby('국가')['방문객수'].sum().idxmax()
max_country_count = int(df_disp.groupby('국가')['방문객수'].sum().max())

colA, colB, colC = st.columns([1.5, 1, 1])
colA.metric("표시된 총 방문객 수", f"{total_visitors:,}")
colB.metric("표시된 국가 수", f"{unique_countries}")
colC.metric("최다 방문 국가", f"{max_country} ({max_country_count:,})")

# --- 그래프 ---
st.markdown("## 그래프")

# 라인 차트
if len(selected_countries) == 0:
    st.info("좌측에서 하나 이상의 국가를 선택하세요.")
else:
    df_line = df_long[(df_long['연도'] == selected_year) & (df_long['국가'].isin(selected_countries))]
    fig_line = px.line(
        df_line.sort_values('해당연월'),
        x='해당연월',
        y='방문객수',
        color='국가',
        markers=True,
        title="선택된 국가 월별 추세"
    )
    fig_line.update_layout(legend_title_text='국가', hovermode='x unified')
    st.plotly_chart(fig_line, use_container_width=True)

# 스택드 영역
st.markdown("### 전체 구성(스택드 영역)")
df_area = df_disp.groupby(['해당연월', '국가'], as_index=False)['방문객수'].sum()
df_pivot = df_area.pivot_table(index='해당연월', columns='국가', values='방문객수', fill_value=0)

fig_area = go.Figure()
for country in df_pivot.columns:
    fig_area.add_trace(go.Scatter(
        x=df_pivot.index,
        y=df_pivot[country],
        stackgroup='one',
        name=country
    ))
fig_area.update_layout(title="국가별 누적/스택드 영역", xaxis_title="월", yaxis_title="방문객수")
st.plotly_chart(fig_area, use_container_width=True)

# 특정 월 분석
if selected_month != "전체" and show_month:
    st.markdown(f"### {selected_year}년 {selected_month}월 방문객 국가별 분포")
    df_month = df_long[(df_long['연도'] == selected_year) & (df_long['월'] == int(selected_month))]
    df_month_agg = df_month.groupby('국가', as_index=False)['방문객수'].sum().sort_values('방문객수', ascending=False)

    fig_bar = px.bar(df_month_agg, x='국가', y='방문객수',
                     title=f"{selected_year}-{selected_month} 국가별 방문객 수")
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_sun = px.sunburst(df_month_agg, path=['국가'], values='방문객수',
                          title="국가별 구성 비중")
    st.plotly_chart(fig_sun, use_container_width=True)

# Top 10 국가
st.markdown("### 상위 방문국 Top 10")
df_top = df_disp.groupby('국가', as_index=False)['방문객수'].sum()\
               .sort_values('방문객수', ascending=False).head(10)
fig_top = px.bar(df_top, x='국가', y='방문객수', text='방문객수',
                 title="Top 10 국가")
fig_top.update_traces(texttemplate='%{text:,}', textposition='outside')
st.plotly_chart(fig_top, use_container_width=True)

# 데이터 표
with st.expander("데이터 표 보기 (필터 적용)"):
    st.dataframe(df_disp.sort_values(['해당연월', '국가']).reset_index(drop=True),
                 use_container_width=True)

st.markdown("---")
st.markdown("#### 사용법")
st.markdown("""
- 이 파일은 `pages/07_제주_외국인관광객.py` 로 저장하세요.
- 상위 폴더(레포지토리 루트)에 반드시 `tour.csv` 파일을 올려주세요.
- Streamlit Cloud에서 자동으로 페이지로 표시됩니다.
""")
