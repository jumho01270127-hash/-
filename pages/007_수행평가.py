import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="제주 외국인 관광객 대시보드", layout="wide")

# -----------------------------
# 1. 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("제주특별자치도_외국인관광객현황_20250319.csv", encoding="cp949")

df = load_data()

st.title("📊 제주특별자치도 외국인 관광객 대시보드")
st.markdown("---")

# -----------------------------
# 2. 기본 데이터 전처리
# -----------------------------
# 날짜 컬럼이 있으면 변환
date_cols = [c for c in df.columns if "월" in c or "날짜" in c]
if date_cols:
    df["월"] = pd.to_datetime(df[date_cols[0]], errors="coerce")
    df["연도"] = df["월"].dt.year
    df["month_num"] = df["월"].dt.month

# 국가, 인종 컬럼 추정
country_col = [c for c in df.columns if "국가" in c or "country" in c.lower()]
race_col = [c for c in df.columns if "인종" in c or "race" in c.lower()]
visitor_col = [c for c in df.columns if "수" in c or "객" in c]

country_col = country_col[0] if country_col else None
race_col = race_col[0] if race_col else None
visitor_col = visitor_col[0] if visitor_col else None

# -----------------------------
# 3. 국가별 방문객 TOP 차트
# -----------------------------
st.subheader("🌍 국가별 방문객 TOP 랭킹")

if country_col and visitor_col:
    top_n = st.slider("표시할 국가 수", 3, 20, 10)
    top_df = df.groupby(country_col)[visitor_col].sum().nlargest(top_n).reset_index()

    fig_top = px.bar(
        top_df,
        x=country_col,
        y=visitor_col,
        color=country_col,
        title=f"국가별 방문객 TOP {top_n}",
    )
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.error("국가 또는 방문객 수 컬럼을 찾지 못했습니다.")

st.markdown("---")

# -----------------------------
# 4. 월별 국가별 추세 그래프
# -----------------------------
st.subheader("📅 월별 국가별 방문객 추세")

if country_col and visitor_col and "month_num" in df.columns:
    selected_countries = st.multiselect(
        "국가 선택",
        options=df[country_col].unique(),
        default=df[country_col].unique()[:5]
    )

    filter_df = df[df[country_col].isin(selected_countries)]

    fig_trend = px.line(
        filter_df,
        x="month_num",
        y=visitor_col,
        color=country_col,
        markers=True,
        title="월별 국가별 추세 그래프"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.error("월/국가 데이터가 충분하지 않습니다.")

st.markdown("---")

# -----------------------------
# 5. 인종별 방문객 그래프
# -----------------------------
st.subheader("👥 인종별 방문객 현황")

if race_col and visitor_col:
    race_df = df.groupby(race_col)[visitor_col].sum().reset_index()

    fig_race = px.bar(
        race_df,
        x=race_col,
        y=visitor_col,
        color=race_col,
        title="인종별 방문객 수"
    )
    st.plotly_chart(fig_race, use_container_width=True)
else:
    st.info("인종 데이터가 없습니다.")

st.markdown("---")

# -----------------------------
# 6. 계절별 방문객 그래프 + 버튼
# -----------------------------
st.subheader("🍀 계절별 방문객 분석")

if "month_num" in df.columns:
    def season(month):
        if month in [3, 4, 5]: return "봄"
        if month in [6, 7, 8]: return "여름"
        if month in [9, 10, 11]: return "가을"
        return "겨울"

    df["계절"] = df["month_num"].apply(season)

    st.markdown("### 계절 선택")

    col1, col2, col3, col4 = st.columns(4)
    buttons = {"봄": col1.button("🌸 봄"),
               "여름": col2.button("🌞 여름"),
               "가을": col3.button("🍁 가을"),
               "겨울": col4.button("❄ 겨울")}

    selected_season = None
    for k, v in buttons.items():
        if v:
            selected_season = k

    if selected_season:
        season_df = df[df["계절"] == selected_season]
        st.write(f"### 🔎 {selected_season} 방문객 데이터")

        fig_season = px.bar(
            season_df.groupby(country_col)[visitor_col].sum().reset_index(),
            x=country_col,
            y=visitor_col,
            color=country_col,
            title=f"{selected_season} 계절 방문객 수"
        )
        st.plotly_chart(fig_season, use_container_width=True)

else:
    st.error("월 데이터를 찾을 수 없습니다.")

