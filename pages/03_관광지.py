# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import folium
from folium.features import CustomIcon
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(page_title="서울 외국인 인기 관광지 Top 10", layout="wide")

st.title("🏙️ 서울 외국인 인기 관광지 Top 10")
st.markdown("서울에서 외국인들이 가장 많이 방문하고 좋아하는 관광지 10곳을 지도에 표시했습니다.\
 마커를 클릭하면 간단한 설명과 가까운 지하철역 정보를 볼 수 있습니다.")

# 관광지 데이터 (이름, 위도, 경도, 카테고리, 설명, 가장 가까운 지하철역)
places = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 3
