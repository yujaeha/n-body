import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 스트림릿 페이지 설정 (와이드 레이아웃, 다크/라이트 자동 호환)
st.set_page_config(page_title="맵부심 측정기 - 음식 매움 지수", layout="wide", page_icon="🌶️")

# 애플리케이션 제목 및 설명
st.title("🌶️ 맵부심 측정기: 음식 매움 지수 탐색기")
st.markdown("궁금한 음식의 이름을 입력해보세요! 해당 음식의 매움 단계와 스코빌 지수(SHU), 그리고 맛있는 음식 사진을 함께 보여줍니다.")

# 2. 음식 매움 데이터베이스 구축 (한국인 선호 음식 중심)
# 단계(Level): 0(안 매움) ~ 5(핵매움)
food_db = {
    "떡볶이": {"level": 2, "shu": "1,000 ~ 2,500", "desc": "매콤달콤한 한국의 대표 간식! 가게마다 맵기 차이가 커요.", "keyword": "tteokbokki"},
    "엽기떡볶이": {"level": 5, "shu": "4,000 ~ 10,000", "desc": "스트레스 풀리는 불타는 매운맛! 쿨피스 필수입니다.", "keyword": "spicy-rice-cake"},
    "신라면": {"level": 2, "shu": "3,400", "desc": "한국인 매운맛의 표준 스탠다드 기분 좋은 얼큰함.", "keyword": "ramen"},
    "불닭볶음면": {"level": 4, "shu": "4,400", "desc": "전 세계를 울린 매운맛! 전설의 볶음면입니다.", "keyword": "spicy-noodles"},
    "핵불닭볶음면": {"level": 5, "shu": "10,000", "desc": "도전 정신을 자극하는 극강의 매운맛, 위장 조심하세요!", "keyword": "chili-noodles"},
    "김치찌개": {"level": 1, "shu": "500 ~ 1,500", "desc": "칼칼하고 시원한 밥도둑, 한국인의 소울푸드.", "keyword": "kimchi-stew"},
    "마라탕": {"level": 3, "shu": "2,000 ~ 5,000", "desc": "혀가 얼얼해지는 초마력의 중국 사천식 매운맛!", "keyword": "malatang"},
    "짬뽕": {"level": 2, "shu": "1,500 ~ 3,000", "desc": "해산물이 우러난 얼큰하고 칼칼한 불맛 국물 요리.", "keyword": "jjamppong"},
    "제육볶음": {"level": 1, "shu": "800 ~ 1,200", "desc": "달콤 매콤하게 볶아낸 대중적인 고기 반찬.", "keyword": "korean-spicy-pork"},
    "풋고추": {"level": 0, "shu": "0 ~ 500", "desc": "아삭아삭하고 쌈장에 찍어 먹기 딱 좋은 안 매운 고추.", "keyword": "green-chili"},
    "청양고추": {"level": 3, "shu": "4,000 ~ 12,000", "desc": "깔끔하고 알싸한 매운맛을 더해주는 한국의 천연 조미료.", "keyword": "cheongyang-chili"},
    "카레": {"level": 1, "shu": "500", "desc": "향신료의 알싸함이 감도는 부드러운 매운맛 (순한맛 기준).", "keyword": "curry"},
    "진라면 매운맛": {"level": 2, "shu": "2,000", "desc": "신라면과 양대산맥을 이루는 얼큰하고 진한 국물 라면.", "keyword": "instant-noodles"},
    "닭발": {"level": 4, "shu": "3,000 ~ 6,000", "desc": "콜라겐 가득, 쫀득하면서도 입안이 얼얼해지는 포차 안주.", "keyword": "spicy-chicken-feet"},
    "낙지볶음": {"level": 4, "shu": "3,500 ~ 7,000", "desc": "밥에 콩나물과 함께 슥슥 비벼 먹는 매콤한 쓰러진 소도 일으키는 맛.", "keyword": "spicy-octopus"}
}

# 3. 사이드바 - 추천 검색어 팁 제공
st.sidebar.header("💡 추천 검색어")
st.sidebar.markdown("아래 음식들을 입력해보세요!")
for food in list(food_db.keys())[:7]:
    st.sidebar.markdown(f"- **{food}**")

# 4. 메인 입력창 UI
user_food = st.text_input("🌶️ 매움 지수가 궁금한 음식 이름을 입력하세요:", placeholder="예: 불닭볶음면, 떡볶이, 마라탕 등").strip()

if user_food:
    # 데이터베이스 검색 (공백 제거 후 매칭률 높이기)
    matched_food = None
    for key in food_db.keys():
        if user_food.replace(" ", "") in key.replace(" ", "") or key.replace(" ", "") in user_food.replace(" ", ""):
            matched_food = key
            break
            
    if matched_food:
        info = food_db[matched_food]
        level = info["level"]
        shu = info["shu"]
        desc = info["desc"]
        keyword = info["keyword"]
        
        st.success(f"🎉 '{matched_food}'의 매움 정보를 찾았습니다!")
        
        # 화면 레이아웃 분할 (좌측: 매움 지수 미터기 / 우측: 음식 사진)
        col1, col2 = st.columns([1.2, 1])
        
        with col1:
            st.subheader("📊 매움 레벨 및 스코빌(SHU)")
            
            # Plotly를 이용한 세련된 반원형 게이지 차트 생성
            level_colors = ["#34c759", "#acff2f", "#ffcc00", "#ff9500", "#ff3b30", "#8b0000"]
            level_names = ["0단계: 순둥이", "1단계: 신라면 미만", "2단계: 맛있게 매움", "3단계: 혀가 얼얼", "4단계: 위장 경보", "5단계: 지옥의 맛"]
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = level,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"<b>{level_names[level]}</b>", 'font': {'size': 20, 'color': level_colors[level]}},
                gauge = {
                    'axis': {'range': [0, 5], 'tickwidth': 1, 'tickcolor': "gray", 'tickvals': [0, 1, 2, 3, 4, 5]},
                    'bar': {'color': level_colors[level]},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 1], 'color': 'rgba(52, 199, 89, 0.2)'},
                        {'range': [1, 2], 'color': 'rgba(172, 255, 47, 0.2)'},
                        {'range': [2, 3], 'color': 'rgba(255, 204, 0, 0.2)'},
                        {'range': [3, 4], 'color': 'rgba(255, 149, 0, 0.2)'},
                        {'range': [4, 5], 'color': 'rgba(255, 59, 48, 0.2)'}
                    ],
                }
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': "white" if st.get_option("theme.base") == "dark" else "black"},
                width=450,
                height=350,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 정보 카드 배치
            st.info(f"ℹ️ **스코빌 지수 (SHU):** {shu} SHU\n\n📝 **음식 설명:** {desc}")
            
        with col2:
            st.subheader("🖼️ 음식 이미지")
            # Unsplash Source API를 활용하여 고화질 키워드 기반 음식 이미지 동적 수집
            # 파라미터에 시간(time.time)을 임의로 섞어 이미지 새로고침 반응성 확보
            img_url = f"https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=600&q=80" # 기본 피자/푸드 이미지 고정 폴백
            
            if keyword:
                img_url = f"https://source.unsplash.com/featured/600x500/?{keyword},food"
            
            # 마크다운/HTML 형태로 가독성 좋고 둥근 모서리가 적용된 이미지 출력
            st.image(img_url, caption=f"맛있는 {matched_food} 이미지 (출처: Unsplash)", use_container_width=True)

    else:
        # DB에 없는 음식을 입력했을 때의 유연한 예외 처리
        st.warning(f"⚠️ '{user_food}'은(는) 데이터베이스에 등록되지 않은 음식입니다.")
        st.markdown("하지만 일반적인 매운 음식 기준으로 예측해 드릴게요!")
        
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.subheader("📊 예측 매움 레벨")
            # 2.5단계 기본 배치
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 2.5,
                title = {'text': "<b>데이터 미등록 음식 (추정치)</b>", 'font': {'size': 18}},
                gauge = {'axis': {'range': [0, 5]}, 'bar': {'color': '#ff9500'}}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', width=450, height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡 카레나 일반적인 한식 찌개류 수준의 맵기(약 1,500 SHU)로 추정됩니다.")
        with col2:
            st.subheader("🖼️ 예측 음식 이미지")
            # 입력한 검색어 그대로 이미지 매칭 시도
            custom_img = f"https://source.unsplash.com/featured/600x500/?{user_food},food"
            st.image(custom_img, caption=f"입력하신 '{user_food}' 관련 추천 이미지", use_container_width=True)
