# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

st.set_page_config(page_title="Seoul Top 10 - Foreigners' Picks", layout="wide")

st.title("서울 외국인 인기 관광지 Top 10 — Folium 지도")
st.markdown("서울에서 외국인에게 인기 있는 관광지 10곳을 지도에 표시합니다. 마커를 클릭하면 간단한 설명이 나옵니다.")

# 관광지 데이터 (이름, 위도, 경도, 카테고리, 설명)
places = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.579617, "lon": 126.977041, "category":"궁궐", "desc":"조선시대의 대표 궁궐. 근정전, 경회루 등이 유명합니다."},
    {"name": "창덕궁 & 후원 (Changdeokgung & Huwon)", "lat": 37.579294, "lon": 126.991043, "category":"궁궐/정원", "desc":"유네스코 세계유산. 후원(비원)으로 유명합니다."},
    {"name": "북촌 한옥마을 (Bukchon Hanok Village)", "lat": 37.582604, "lon": 126.983030, "category":"전통마을", "desc":"전통 한옥이 모여 있는 지역으로 산책하기 좋습니다."},
    {"name": "인사동 (Insadong)", "lat": 37.574372, "lon": 126.985029, "category":"쇼핑/문화", "desc":"전통 공예품, 갤러리, 찻집 등이 많은 문화거리입니다."},
    {"name": "명동 (Myeongdong)", "lat": 37.560975, "lon": 126.986015, "category":"쇼핑/음식", "desc":"쇼핑과 길거리 음식이 발달한 대표 관광 상권입니다."},
    {"name": "N서울타워 (N Seoul Tower, Namsan)", "lat": 37.551169, "lon": 126.988227, "category":"전망/탑", "desc":"서울 전망을 한눈에 볼 수 있는 타워. 케이블카/산책 코스와 연결됩니다."},
    {"name": "홍대 (Hongdae)", "lat": 37.556241, "lon": 126.923998, "category":"젊음/예술", "desc":"인디 음악, 길거리 공연, 카페와 클럽이 모여 있는 지역입니다."},
    {"name": "동대문디자인플라자 (DDP, Dongdaemun Design Plaza)", "lat": 37.566324, "lon": 127.009210, "category":"디자인/야경", "desc":"독특한 건축물과 야간 조명, 패션 타운이 유명합니다."},
    {"name": "롯데월드타워 (Lotte World Tower / Jamsil)", "lat": 37.513068, "lon": 127.102539, "category":"쇼핑/전망", "desc":"한국에서 가장 높은 타워 중 하나. 전망대와 쇼핑몰이 있습니다."},
    {"name": "코엑스 & 봉은사 (COEX & Bongeunsa, Gangnam)", "lat": 37.512091, "lon": 127.058567, "category":"컨벤션/사찰", "desc":"대형 쇼핑몰(코엑스)과 전통 사찰(봉은사)이 근접해 있습니다."}
]

df = pd.DataFrame(places)

# 사이드바: 카테고리 필터 및 리스트 보기
st.sidebar.header("필터")
categories = ["All"] + sorted(df['category'].unique().tolist())
selected_cat = st.sidebar.selectbox("카테고리 선택", categories)

if selected_cat != "All":
    df_display = df[df['category'] == selected_cat].reset_index(drop=True)
else:
    df_display = df.copy()

st.sidebar.markdown("---")
st.sidebar.header("장소 목록")
for i, row in df_display.iterrows():
    st.sidebar.write(f"{i+1}. {row['name']}")

# 초기 지도 중심: 서울 중심 좌표 (약)
seoul_center = [37.5665, 126.9780]
m = folium.Map(location=seoul_center, zoom_start=12, control_scale=True)

# 마커 클러스터 추가
marker_cluster = MarkerCluster().add_to(m)

# 색상 매핑 (간단)
color_map = {
    "궁궐": "darkpurple",
    "궁궐/정원": "purple",
    "전통마을": "green",
    "쇼핑/문화": "blue",
    "쇼핑/음식": "cadetblue",
    "전망/탑": "red",
    "젊음/예술": "orange",
    "디자인/야경": "pink",
    "쇼핑/전망": "darkblue",
    "컨벤션/사찰": "beige"
}

# 마커 추가
for _, r in df_display.iterrows():
    popup_html = f"""
    <b>{r['name']}</b><br>
    <i>{r['category']}</i><br>
    <p style="max-width:200px">{r['desc']}</p>
    """
    folium.Marker(
        location=[r['lat'], r['lon']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=r['name'],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(marker_cluster)

# 지도 렌더링 (streamlit_folium 이용)
st.subheader("지도 (마커를 클릭하세요)")
map_data = st_folium(m, width="100%", height=650)

# 하단: 테이블 출력 및 CSV 다운로드
st.subheader("관광지 목록")
st.dataframe(df_display[['name','category','lat','lon','desc']].rename(columns={
    'name':'이름','category':'카테고리','lat':'위도','lon':'경도','desc':'설명'
}), use_container_width=True)

# CSV 다운로드
@st.cache_data
def to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8')

csv_bytes = to_csv_bytes(df_display)
st.download_button("CSV로 다운로드", data=csv_bytes, file_name="seoul_top10_places.csv", mime="text/csv")

st.markdown("---")
st.caption("데이터: 예시용으로 구성되었습니다. 필요하면 장소/설명/좌표를 업데이트해 드립니다.")
