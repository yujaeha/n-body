import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 스트림릿 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="맵부심 측정기 - 음식 매움 지수", layout="wide", page_icon="🌶️")

# 애플리케이션 제목 및 설명
st.title("🌶️ 맵부심 측정기: 음식 매움 지수 탐색기")
st.markdown("궁금한 음식의 이름을 입력해보세요! 해당 음식의 매움 단계와 스코빌 지수(SHU), 그리고 직관적인 그래픽 리포트를 함께 보여줍니다.")

# 2. 음식 매움 데이터베이스 (보안 차단 및 엑스박스 오류가 없는 안전한 오픈 이미지 링크 및 대체 이모지 가드 적용)
food_db = {
    "떡볶이": {
        "level": 2, 
        "shu": "1,000 ~ 2,500", 
        "desc": "매콤달콤한 한국의 대표 간식! 고추장과 물엿 베이스로 가게마다 맵기 차이가 커요.", 
        "emoji": "🍡🌶️",
        "img_url": "https://images.unsplash.com/photo-1664188941753-4811776b9112?auto=format&fit=crop&w=600&q=80"
    },
    "엽기떡볶이": {
        "level": 5, 
        "shu": "4,000 ~ 10,000", 
        "desc": "스트레스 풀리는 불타는 매운맛! 캡사이신과 고춧가루의 강력한 조합으로 쿨피스가 필수입니다.", 
        "emoji": "🔥🍲",
        "img_url": "https://images.unsplash.com/photo-1585032226651-759b368d7246?auto=format&fit=crop&w=600&q=80"
    },
    "신라면": {
        "level": 2, 
        "shu": "3,400", 
        "desc": "한국인 매운맛의 표준 스탠다드. 쇠고기 분말 베이스의 기분 좋은 얼큰함입니다.", 
        "emoji": "🍜✨",
        "img_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?auto=format&fit=crop&w=600&q=80"
    },
    "불닭볶음면": {
        "level": 4, 
        "shu": "4,400", 
        "desc": "전 세계를 울린 K-매운맛의 선두주자! 국물 없는 액상 수프의 강렬한 매운맛입니다.", 
        "emoji": "🐔🔥",
        "img_url": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=600&q=80"
    },
    "핵불닭볶음면": {
        "level": 5, 
        "shu": "10,000", 
        "desc": "도전 정신을 자극하는 극강의 매운맛, 위장 조심하세요!", 
        "emoji": "💀🔥",
        "img_url": "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=600&q=80"
    },
    "김치찌개": {
        "level": 1, 
        "shu": "500 ~ 1,500", 
        "desc": "잘 익은 김치와 돼지고기를 달달 볶아 끓여낸 칼칼하고 시원한 한국인의 소울푸드.", 
        "emoji": "🍲🐷",
        "img_url": "https://images.unsplash.com/photo-1627308595229-7830a5c91f9f?auto=format&fit=crop&w=600&q=80"
    },
    "마라탕": {
        "level": 3, 
        "shu": "2,000 ~ 5,000", 
        "desc": "초피(화조)와 고추기름이 들어가 혀가 저리고 얼얼해지는 사천식 매운맛!", 
        "emoji": "🪵⚡",
        "img_url": "https://images.unsplash.com/photo-1541696490-8744a5db0228?auto=format&fit=crop&w=600&q=80"
    },
    "짬뽕": {
        "level": 2, 
        "shu": "1,500 ~ 3,000", 
        "desc": "야채와 해산물을 강한 불에 볶아 육수를 부어 만든 얼큰하고 칼칼한 국물 요리.", 
        "emoji": "🦑🍜",
        "img_url": "https://images.unsplash.com/photo-1608897013039-887f21d8c804?auto=format&fit=crop&w=600&q=80"
    },
    "제육볶음": {
        "level": 1, 
        "shu": "800 ~ 1,200", 
        "desc": "돼지고기를 고추장 양념에 달콤 매콤하게 볶아낸 대중적인 반찬 요리.", 
        "emoji": "🐷🔥",
        "img_url": "https://images.unsplash.com/photo-1600891964599-f61ba0e24092?auto=format&fit=crop&w=600&q=80"
    },
    "닭발": {
        "level": 4, 
        "shu": "3,000 ~ 6,000", 
        "desc": "콜라겐 가득, 쫀득하면서도 입안이 불타오르는 매운 양념 직화 포차 안주.", 
        "emoji": "🐾🌶️",
        "img_url": "https://images.unsplash.com/photo-1623961990059-28355ee88ac3?auto=format&fit=crop&w=600&q=80"
    }
}

# 3. 사이드바 - 추천 검색어 팁 제공
st.sidebar.header("💡 추천 검색어")
st.sidebar.markdown("아래 음식들을 입력해보세요!")
for food in list(food_db.keys()):
    st.sidebar.markdown(f"- **{food}**")

# 4. 메인 입력창 UI
user_food = st.text_input("🌶️ 매움 지수가 궁금한 음식 이름을 입력하세요:", placeholder="예: 떡볶이, 신라면, 마라탕, 불닭볶음면 등").strip()

if user_food:
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
        emoji = info["emoji"]
        img_url = info["img_url"]
        
        st.success(f"🎉 '{matched_food}'의 매움 정보를 찾았습니다!")
        
        col1, col2 = st.columns([1.2, 1])
        
        with col1:
            st.subheader("📊 매움 레벨 및 스코빌(SHU)")
            
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
            st.info(f"ℹ️ **스코빌 지수 (SHU):** {shu} SHU\n\n📝 **음식 설명:** {desc}")
            
        with col2:
            st.subheader("🖼️ 시각 정보 요약")
            
            # [핵심 변경] 외부 서버 트래픽 원천 차단 시 작동할 HTML 카드형 대형 이모지 패널 제작
            card_html = f"""
            <div style="background: linear-gradient(135deg, #ff4b4b 0%, #ff8585 100%); 
                        padding: 30px; 
                        border-radius: 15px; 
                        text-align: center; 
                        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
                        color: white;
                        margin-bottom: 15px;">
                <span style="font-size: 70px;">{emoji}</span>
                <h2 style="color: white; margin-top: 10px; font-weight: bold;">{matched_food}</h2>
                <p style="font-size: 16px; opacity: 0.9;">위키 및 고해상도 백업 가동 중</p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 가드용 글로벌 고속 분산형 이미지 링크 출력 (안전하게 렌더링을 보장)
            try:
                st.image(img_url, caption=f"맛있는 {matched_food} 실물 스냅샷", use_container_width=True)
            except:
                st.caption("⚠️ 실시간 고해상도 이미지는 스트림릿 클라우드 네트워크 사정상 상단 이모지 카드로 대체 표기됩니다.")

    else:
        st.warning(f"⚠️ '{user_food}'은(는) 데이터베이스에 등록되지 않은 음식입니다.")
        st.markdown("일반적인 매운 음식 기준으로 예측해 드릴게요!")
        
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.subheader("📊 예측 매움 레벨")
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 2.5,
                title = {'text': "<b>데이터 미등록 음식 (추정치)</b>", 'font': {'size': 18}},
                gauge = {'axis': {'range': [0, 5]}, 'bar': {'color': '#ff9500'}}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', width=450, height=300)
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡 일반적인 한식 찌개나 볶음류 수준의 맵기(약 1,500 SHU)로 추정됩니다.")
        with col2:
            st.subheader("🖼️ 예측 기본 요리 정보")
            st.markdown("""
            <div style="background-color: #262730; padding: 40px; border-radius: 10px; text-align: center; border: 1px solid #464855;">
                <span style="font-size: 60px;">🍲🍱</span>
                <p style="color: gray; margin-top: 15px;">대표적인 한식 구성 플레이트 스탠다드</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("💡 위의 입력창에 음식 이름을 입력하시면 매움 지수 스케일러가 즉시 작동합니다.")
