import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(page_title="서울 외국인 인기 관광지 Top 10", layout="wide")

# 타이틀
st.title("🏙️ 서울 외국인 인기 관광지 Top 10")
st.markdown("""
서울에서 외국인들이 가장 많이 방문하는 관광지 10곳을 지도에 표시했습니다.  
마커를 클릭하면 설명과 가까운 지하철역을 볼 수 있습니다.
""")

# 데이터
places = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.579617, "lon": 126.977041, "category": "궁궐",
     "desc": "조선시대 대표 궁궐로, 근정전과 경회루 등 전통 건축미가 뛰어난 명소입니다.",
     "subway": "경복궁역 (3호선) 도보 5분"},
    {"name": "창덕궁 & 후원 (Changdeokgung & Huwon)", "lat": 37.579294, "lon": 126.991043, "category": "궁궐/정원",
     "desc": "유네스코 세계문화유산으로 지정된 궁궐로 후원이 유명합니다.",
     "subway": "안국역 (3호선) 도보 10분"},
    {"name": "북촌 한옥마을 (Bukchon Hanok Village)", "lat": 37.582604, "lon": 126.983030, "category": "전통마을",
     "desc": "전통 한옥이 즐비한 한국 고유의 전통 마을입니다.",
     "subway": "안국역 (3호선) 도보 5분"},
    {"name": "인사동 (Insadong)", "lat": 37.574372, "lon": 126.985029, "category": "문화거리",
     "desc": "전통 공예품, 갤러리, 찻집 등이 모인 문화거리입니다.",
     "subway": "종각역 (1호선) 도보 7분"},
    {"name": "명동 (Myeongdong)", "lat": 37.560975, "lon": 126.986015, "category": "쇼핑거리",
     "desc": "서울 대표 쇼핑거리로 외국인 관광객의 필수 방문지입니다.",
     "subway": "명동역 (4호선) 도보 3분"},
    {"name": "N서울타워 (N Seoul Tower)", "lat": 37.551169, "lon": 126.988227, "category": "전망/탑",
     "desc": "서울의 전망을 한눈에 볼 수 있는 대표 명소입니다.",
     "subway": "명동역 → 남산 케이블카 이용"},
    {"name": "홍대 (Hongdae)", "lat": 37.556241, "lon": 126.923998, "category": "예술/거리",
     "desc": "젊음의 거리로 인디 음악과 다양한 공연으로 유명합니다.",
     "subway": "홍대입구역 (2호선) 도보 3분"},
    {"name": "동대문디자인플라자 (DDP)", "lat": 37.566324, "lon": 127.009210, "category": "디자인/야경",
     "desc": "미래적인 건축 디자인과 야경이 유명한 랜드마크입니다.",
     "subway": "동대문역사문화공원역 도보 2분"},
    {"name": "롯데월드타워 (Lotte World Tower)", "lat": 37.513068, "lon": 127.102539, "category": "쇼핑/전망",
     "desc": "초고층 빌딩으로 쇼핑·전망·호텔이 함께 있는 복합 공간입니다.",
     "subway": "잠실역 도보 2분"},
    {"name": "코엑스 & 봉은사", "lat": 37.512091, "lon": 127.058567, "category": "문화/사찰",
     "desc": "현대적인 코엑스와 전통 사찰 봉은사가 공존하는 지역입니다.",
     "subway": "삼성역 도보 5분"}
]

df = pd.DataFrame(places)

# 사이드바 필터
st.sidebar.header("필터")
categories = ["All"] + sorted(df["category"].unique())
selected = st.sidebar.selectbox("카테고리 선택", categories)
df_display = df if selected == "All" else df[df["category"] == selected]

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

color_map = {
    "궁궐": "purple",
    "궁궐/정원": "darkpurple",
    "전통마을": "green",
    "문화거리": "blue",
    "쇼핑거리": "cadetblue",
    "전망/탑": "red",
    "예술/거리": "orange",
    "디자인/야경": "lightred",
    "쇼핑/전망": "darkblue",
    "문화/사찰": "gray"
}

# 마커 추가
for _, r in df_display.iterrows():
    html = """
    <div style="width:200px;">
        <b>{}</b><br>
        <i>{}</i><br>
        <p style="font-size:13px;">{}</p>
        <p><b>{}</b></p>
    </div>
    """.format(r["name"], r["category"], r["desc"], r["subway"])

    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=10,
        color=color_map.get(r["category"], "blue"),
        fill=True,
        fill_opacity=0.8,
        fill_color=color_map.get(r["category"], "blue"),
        popup=folium.Popup(html, max_width=250),
        tooltip=r["name"]
    ).add_to(marker_cluster)

# 지도 출력
st.subheader("🗺 관광지도")
st_folium(m, width="100%", height=650)

# 상세 설명
st.subheader("📍 관광지별 설명")
for i, row in df_display.iterrows():
    st.markdown("### {}. {}".format(i + 1, row["name"]))
    st.write("**카테고리:** {}".format(row["category"]))
    st.write("**지하철역:** {}".format(row["subway"]))
    st.write("**설명:** {}".format(row["desc"]))
    st.markdown("---")

# 테이블
st.subheader("📋 관광지 데이터 요약")
st.dataframe(df_display, use_container_width=True)

st.caption("※ 실제 도보 시간과 거리는 약간의 차이가 있을 수 있습니다.")
