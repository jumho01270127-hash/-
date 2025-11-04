import streamlit as st
st.title('나의 첫 웹 서비스 만들기!')
name=st.text_input('이름을 말해주세요')
menu=st.selectbox('좋아하는 음식을 선택하시기',['재은','우주','응호'])
if st.button('인사생성'):
  st.info(name+'안녕하시기')
  st.warning(menu+'을(를) 종아하시기,나는 별로')
  st.error('반갑수다')
