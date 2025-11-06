import streamlit as st

st.set_page_config(page_title="MBTI 맞춤 책·영화 추천 💫", page_icon="📚", layout="centered")

st.title("💫 MBTI별 맞춤 책 & 영화 추천 💫")
st.write("당신의 MBTI를 선택하면, 딱 어울리는 책 2권과 영화 2편을 추천해드릴게요 😄")

# MBTI 리스트
mbti_list = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

choice = st.selectbox("당신의 MBTI는 무엇인가요? 👇", mbti_list)

# MBTI별 추천 데이터
recommendations = {
    "INTJ": {
        "books": [("1984 - 조지 오웰", "미래를 예리하게 분석하는 INTJ의 통찰력과 잘 어울려요."),
                  ("데미안 - 헤르만 헤세", "자기 성찰과 성장의 여정을 즐기는 INTJ에게 딱이에요.")],
        "movies": [("인셉션", "복잡한 구조와 철학적인 메시지를 좋아하는 INTJ의 취향 저격 🎯"),
                   ("인터스텔라", "논리와 감성이 공존하는 이야기에 빠져들 거예요.")]
    },
    "INFP": {
        "books": [("어린 왕자 - 생텍쥐페리", "감성 깊은 INFP의 마음을 따뜻하게 어루만져줘요."),
                  ("월든 - 헨리 데이비드 소로", "자연과 자기 내면을 사랑하는 INFP에게 어울려요.")],
        "movies": [("월-E", "조용하지만 따뜻한 감정선이 INFP의 마음을 두드릴 거예요 💫"),
                   ("어바웃 타임", "사랑과 삶의 의미를 곱씹게 하는 잔잔한 영화예요.")]
    },
    "ENTP": {
        "books": [("호밀밭의 파수꾼 - 제롬 D. 샐린저", "세상을 다르게 보는 ENTP의 시선과 닮았어요."),
                  ("이기적 유전자 - 리처드 도킨스", "논쟁과 아이디어를 즐기는 ENTP의 지적 호기심 자극!")],
        "movies": [("아이언맨", "창의적이고 대담한 ENTP의 캐릭터와 딱 맞아요 ⚡"),
                   ("캐치 미 이프 유 캔", "빠른 전개와 재치 있는 머리싸움을 좋아하는 ENTP에게 굿.")]
    },
    "ISFJ": {
        "books": [("작은 아씨들 - 루이자 메이 올컷", "가족과 따뜻한 관계를 소중히 여기는 ISFJ에게 어울려요."),
                  ("연금술사 - 파울로 코엘료", "자신의 길을 조용히 찾는 여정을 응원해줘요.")],
        "movies": [("센과 치히로의 행방불명", "섬세하고 따뜻한 감성을 가진 ISFJ에게 잘 맞아요 🐉"),
                   ("인사이드 아웃", "감정을 이해하고 공감하는 ISFJ의 마음과 닮았어요.")]
    },
    "ENFP": {
        "books": [("알렉산더와 이상한 하루 - 주디스 비오스트", "에너지 넘치고 자유로운 ENFP에게 유쾌한 책이에요."),
                  ("이토록 평범한 미래 - 김연수", "상상력과 감성이 넘치는 ENFP의 마음에 잔잔히 스며들 거예요.")],
        "movies": [("라라랜드", "꿈과 사랑, 감성까지 다 있는 ENFP의 인생 영화 🎶"),
                   ("월터의 상상은 현실이 된다", "모험을 꿈꾸는 ENFP의 심장을 두근거리게 해요.")]
    },
    # 필요 시 다른 MBTI도 여기에 추가 가능
}

# 선택된 MBTI의 추천 보여주기
if choice in recommendations:
    st.subheader(f"📘 {choice}에게 추천하는 책")
    for book, reason in recommendations[choice]["books"]:
        st.markdown(f"**{book}** — {reason}")
    
    st.subheader(f"🎬 {choice}에게 추천하는 영화")
    for movie, reason in recommendations[choice]["movies"]:
        st.markdown(f"**{movie}** — {reason}")
else:
    st.info("이 MBTI는 아직 데이터가 준비 중이에요! 조금만 기다려주세요 😅")

st.markdown("---")
st.caption("📚 추천은 재미로 보는 용도예요! 마음에 드는 작품을 찾아보는 계기로 삼아보세요 💕")
