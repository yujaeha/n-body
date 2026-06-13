import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 스트림릿 페이지 설정
st.set_page_config(page_title="맵부심 측정기 - 음식 매움 지수", layout="wide", page_icon="🌶️")

st.title("🌶️ 맵부심 측정기: 음식 매움 지수 탐색기")
st.markdown("궁금한 음식의 이름을 입력해보세요! 외부 서버 차단 없이 100% 안전하게 동작하는 시각 리포트와 매움 단계를 보여줍니다.")

# 2. 내장형 그래픽 카드 데이터 (외부 주소 완전 배제, 인터넷 차단 영향 0%)
# 이미지 서버가 차단되어도 브라우저가 직접 그려내는 대형 그래픽 컴포넌트 구조입니다.
food_db = {
    "떡볶이": {
        "level": 2, "shu": "1,000 ~ 2,500", 
        "desc": "매콤달콤한 한국의 대표 간식! 고추장과 물엿 베이스로 가게마다 맵기 차이가 커요.",
        "bg_color": "linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%)", "emoji": "🍡", "status": "맛있게 매움"
    },
    "엽기떡볶이": {
        "level": 5, "shu": "4,000 ~ 10,000", 
        "desc": "스트레스 풀리는 불타는 매운맛! 캡사이신과 고춧가루의 강력한 조합으로 쿨피스가 필수입니다.",
        "bg_color": "linear-gradient(135deg, #830000 0%, #BA0000 100%)", "emoji": "🔥", "status": "지옥의 극강 매운맛"
    },
    "신라면": {
        "level": 2, "shu": "3,400", 
        "desc": "한국인 매운맛의 표준 스탠다드. 쇠고기 분말 베이스의 기분 좋은 얼큰함입니다.",
        "bg_color": "linear-gradient(135deg, #FF4B2B 0%, #FF8533 100%)", "emoji": "🍜", "status": "얼큰한 표준 매운맛"
    },
    "불닭볶음면": {
        "level": 4, "shu": "4,400", 
        "desc": "전 세계를 울린 K-매운맛의 선두주자! 국물 없는 액상 수프의 강렬한 매운맛입니다.",
        "bg_color": "linear-gradient(135deg, #D31027 0%, #EA384D 100%)", "emoji": "🐔", "status": "위장 경보 발령"
    },
    "핵불닭볶음면": {
        "level": 5, "shu": "10,000", 
        "desc": "도전 정신을 자극하는 극강의 매운맛, 위장 조심하세요!",
        "bg_color": "linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%)", "emoji": "💀", "status": "위험! 도전 금지 수준"
    },
    "김치찌개": {
        "level": 1, "shu": "500 ~ 1,500", 
        "desc": "잘 익은 김치와 돼지고기를 달달 볶아 끓여낸 칼칼하고 시원한 한국인의 소울푸드.",
        "bg_color": "linear-gradient(135deg, #f12711 0%, #f5af19 100%)", "emoji": "🍲", "status": "부담 없는 맵기"
    },
    "마라탕": {
        "level": 3, "shu": "2,000 ~ 5,000", 
        "desc": "초피(화조)와 고추기름이 들어가 혀가 저리고 얼얼해지는 사천식 매운맛!",
        "bg_color": "linear-gradient(135deg, #7A0016 0%, #DD1818 100%)", "emoji": "⚡", "status": "혀가 마비되는 얼얼함"
    },
    "짬뽕": {
        "level": 2, "shu": "1,500 ~ 3,000", 
        "desc": "야채와 해산물을 강한 불에 볶아 육수를 부어 만든 얼큰하고 칼칼한 국물 요리.",
        "bg_color": "linear-gradient(135deg, #FE8C00 0%, #F83600 100%)", "emoji": "🦑", "status": "시원 칼칼한 맛"
    },
    "제육볶음": {
        "level": 1, "shu": "800 ~ 1,200", 
        "desc": "돼지고기를 고추장 양념에 달콤 매콤하게 볶아낸 대중적인 반찬 요리.",
        "bg_color": "linear-gradient(135deg, #FF512F 0%, #DD2476 100%)", "emoji": "🐷", "status": "매콤달콤 밥도둑"
    },
    "닭발": {
        "level": 4, "shu": "3,000 ~ 6,000", 
        "desc": "콜라겐 가득, 쫀득하면서도 입안이 불타오르는 매운 양념 직화 포차 안주.",
        "bg_color": "linear-gradient(135deg, #ED213A 0%, #93291E 100%)", "emoji": "🐾", "status": "입안이 화끈한 안주"
    }
}

# 3. 사이드바 - 추천 검색어
st.sidebar.header("💡 추천 검색어")
for food in list(food_db.keys()):
    st.sidebar.markdown(f"- **{food}**")

# 4. 메인 UI
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
        bg_color = info["bg_color"]
        emoji = info["emoji"]
        status = info["status"]
        
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
            st.subheader("🖼️ 음식 시각 리포트 카탈로그")
            
            # 외부 링크가 전혀 없는 고해상도 내장형 디자인 컴포넌트 렌더링 (엑스박스 절대 불가능)
            card_html = f"""
            <div style="background: {bg_color}; 
                        padding: 50px 20px; 
                        border-radius: 20px; 
                        text-align: center; 
                        box-shadow: 0px 10px 25px rgba(0,0,0,0.3);
                        color: white;
                        font-family: 'Malgun Gothic', sans-serif;
                        margin-top: 15px;">
                <div style="font-size: 100px; margin-bottom: 20px; filter: drop-shadow(0px 5px 5px rgba(0,0,0,0.2));">{emoji}</div>
                <h1 style="color: white; margin: 0px 0px 10px 0px; font-weight: 800; font-size: 36px; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{matched_food}</h1>
                <div style="background-color: rgba(255,255,255,0.2); 
                            display: inline-block; 
                            padding: 8px 20px; 
                            border-radius: 50px; 
                            font-size: 18px; 
                            font-weight: bold;
                            letter-spacing: 1px;
                            box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
                    🔥 {status} (Level {level})
                </div>
                <p style="margin-top: 25px; font-size: 14px; opacity: 0.8; font-weight: 300;">* 스트림릿 안전 가드 모드가 작동 중입니다.</p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

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
            <div style="background: linear-gradient(135deg, #434343 0%, #000000 100%); padding: 60px 20px; border-radius: 20px; text-align: center; color: white;">
                <div style="font-size: 80px;">🍲</div>
                <p style="color: #cccccc; margin-top: 15px; font-size: 18px;">미등록 표준 한식 푸드 세팅</p>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("💡 위의 입력창에 음식 이름을 입력하시면 실시간 매움 지수 스케일러가 즉시 작동합니다.")
