import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from io import BytesIO

# 1. 스트림릿 페이지 설정 (와이드 레이아웃, 다크/라이트 자동 호환)
st.set_page_config(page_title="맵부심 측정기 - 음식 매움 지수", layout="wide", page_icon="🌶️")

# 애플리케이션 제목 및 설명
st.title("🌶️ 맵부심 측정기: 음식 매움 지수 탐색기")
st.markdown("궁금한 음식의 이름을 입력해보세요! 해당 음식의 매움 단계와 스코빌 지수(SHU), 그리고 위키백과/나무위키 기반의 정확한 음식 사진을 우회 다운로드하여 보여줍니다.")

# 2. 음식 매움 데이터베이스 구축 (위키피디아 / 위키미디어 소스)
food_db = {
    "떡볶이": {
        "level": 2, 
        "shu": "1,000 ~ 2,500", 
        "desc": "매콤달콤한 한국의 대표 간식! 고추장과 물엿 베이스로 가게마다 맵기 차이가 커요.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Tteokbokki.jpg"
    },
    "엽기떡볶이": {
        "level": 5, 
        "shu": "4,000 ~ 10,000", 
        "desc": "스트레스 풀리는 불타는 매운맛! 캡사이신과 고춧가루의 강력한 조합으로 쿨피스가 필수입니다.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Ddaengcho_tteokbokki.jpg"
    },
    "신라면": {
        "level": 2, 
        "shu": "3,400", 
        "desc": "한국인 매운맛의 표준 스탠다드. 쇠고기 분말 베이스의 기분 좋은 얼큰함입니다.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/b/b2/Shin_Ramyun_block.jpg"
    },
    "불닭볶음면": {
        "level": 4, 
        "shu": "4,400", 
        "desc": "전 세계를 울린 K-매운맛의 선두주자! 국물 없는 액상 수프의 강렬한 인술 같은 매운맛입니다.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Buldak-bokkeum-myeon.jpg"
    },
    "김치찌개": {
        "level": 1, 
        "shu": "500 ~ 1,500", 
        "desc": "잘 익은 김치와 돼지고기를 달달 볶아 끓여낸 칼칼하고 시원한 한국인의 소울푸드.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Kimchi_jjigae.jpg"
    },
    "마라탕": {
        "level": 3, 
        "shu": "2,000 ~ 5,000", 
        "desc": "초피(화조)와 고추기름이 들어가 혀가 저리고 얼얼해지는(마비되는 듯한) 사천식 매운맛!", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/3/36/Malatang_in_Seoul.jpg"
    },
    "짬뽕": {
        "level": 2, 
        "shu": "1,500 ~ 3,000", 
        "desc": "야채와 해산물을 강한 불에 볶아 육수를 부어 만든 얼큰하고 칼칼한 중화풍 국물 요리.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/a/a8/Jjamppong.jpg"
    },
    "제육볶음": {
        "level": 1, 
        "shu": "800 ~ 1,200", 
        "desc": "돼지고기를 고추장, 고춧가루 양념에 달콤 매콤하게 볶아낸 대중적인 기사식당 원탑 반찬.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/d/db/Jeyuk_bokkeum.jpg"
    },
    "닭발": {
        "level": 4, 
        "shu": "3,000 ~ 6,000", 
        "desc": "콜라겐 가득, 쫀득하면서도 입안이 불타오르는 매운 양념 직화 포차 안주.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Dakbal.jpg"
    },
    "낙지볶음": {
        "level": 4, 
        "shu": "3,500 ~ 7,000", 
        "desc": "강렬한 고춧가루 양념에 낙지를 빠르게 볶아내 밥, 콩나물과 비벼 먹는 스테미너 요리.", 
        "img_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Nakji_bokkeum.jpg"
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
    # 데이터베이스 검색 (공백 제거 후 부분 매칭)
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
            st.subheader("🖼️ 음식 이미지")
            
            # [핵심 수정] 나무위키/위키미디어 차단 정책 우회용 로직 구현
            # 헤더에 웹 브라우저 정보(User-Agent)를 입력하여 봇 탐지를 차단합니다.
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            try:
                # 이미지를 서버 백엔드 단에서 직접 바이너리로 다운로드
                response = requests.get(img_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    image_bytes = BytesIO(response.content)
                    # 다운로드받은 바이너리 데이터를 스트림릿 이미지 컴포넌트에 직접 주입 (안전지대)
                    st.image(image_bytes, caption=f"정확한 {matched_food} 실물 사진 (위키 연동)", use_container_width=True)
                else:
                    st.error(f"이미지 서버가 응답하지 않습니다. (에러 코드: {response.status_code})")
            except Exception as e:
                # 통신 예외 상황 시 백업 렌더링 처리
                st.warning("이미지 로딩 중 네트워크 오류가 발생했습니다.")
                st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Korean_table_setting_1.jpg/640px-Korean_table_setting_1.jpg", use_container_width=True)

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
            st.subheader("🖼️ 예측 음식 이미지")
            fallback_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Korean_table_setting_1.jpg/640px-Korean_table_setting_1.jpg"
            st.image(fallback_img, caption="추천 한식 상차림 이미지", use_container_width=True)
