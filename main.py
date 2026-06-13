import streamlit as st
import googleapiclient.discovery
import googleapiclient.errors
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import os

# 한글 폰트 설정 (스트림릿 클라우드 나눔폰트 경로 설정)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf" # 기본 폴백
if os.path.exists("/usr/share/fonts/nanum/NanumGothic.ttf"):
    FONT_PATH = "/usr/share/fonts/nanum/NanumGothic.ttf"

# 1. 유튜브 영상 ID 추출 함수
def get_video_id(url):
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    return video_id_match.group(1) if video_id_match else None

# 2. 유튜브 댓글 및 작성자 수집 함수 (수정됨)
def get_youtube_comments(video_id, api_key, max_results=100):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    comment_data = [] # (작성자, 댓글내용) 튜플을 담을 리스트
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(max_results, 100),
            textFormat="plainText"
        )
        
        while request and len(comment_data) < max_results:
            response = request.execute()
            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                author = snippet.get("authorDisplayName", "알 수 없는 사용자")
                comment_text = snippet.get("textDisplay", "")
                
                comment_data.append((author, comment_text))
            
            if "nextPageToken" in response and len(comment_data) < max_results:
                request = youtube.commentThreads().list_next(request, response)
            else:
                break
                
        return comment_data
    except googleapiclient.errors.HttpError as e:
        st.error(f"유튜브 API 오류가 발생했습니다: {e}")
        return []

# 3. 텍스트 전처리 및 단어 빈도 계산
def clean_text_and_get_words(comment_data):
    # 댓글 내용만 합치기
    full_text = " ".join([item[1] for item in comment_data])
    
    # 한글, 영문, 숫자만 남기고 제거
    cleaned_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', full_text)
    words = cleaned_text.split()
    
    # 분석에서 제외할 의미 없는 단어(불용어) 설정
    stopwords = {'그냥', '진짜', '너무', '보고', '영상이', '영상', '완전', '시청', '구독', '좋아요', '정말', '항상', '대박'}
    words = [word for word in words if len(word) > 1 and word not in stopwords]
    
    return words

# --- 스트림릿 UI 시작 ---
st.set_page_config(page_title="유튜브 댓글 심층 분석기", layout="wide")

st.title("📊 유튜브 댓글 작성자 파악 및 키워드 분석기")
st.markdown("유튜브 링크를 통해 댓글 작성자와 내용을 수집하고, 가장 많이 사용된 핵심 단어와 워드 클라우드를 생성합니다.")

# 사이드바 설정
st.sidebar.header("⚙️ 설정")
api_key = st.sidebar.text_input("YouTube API Key를 입력하세요", type="password")
max_comments = st.sidebar.slider("수집할 댓글 수", min_value=20, max_value=500, value=100, step=20)

# 메인 입력창
video_url = st.text_input("유튜브 영상 링크(URL)를 입력하세요", placeholder="https://www.youtube.com/watch?v=...")

if st.button("🚀 댓글 및 작성자 분석 시작"):
    if not api_key:
        st.warning("사이드바에 YouTube API Key를 입력해주세요.")
    elif not video_url:
        st.warning("유튜브 영상 링크를 입력해주세요.")
    else:
        video_id = get_video_id(video_url)
        
        if not video_id:
            st.error("올바른 유튜브 링크 형식이 아닙니다. 확인 후 다시 시도해주세요.")
        else:
            with st.spinner("유튜브에서 데이터를 가져와 열심히 분석 중입니다..."):
                # 댓글 데이터 수집 (작성자, 내용)
                comment_data = get_youtube_comments(video_id, api_key, max_comments)
                
                if comment_data:
                    st.success(f"총 {len(comment_data)}개의 댓글을 성공적으로 수집했습니다!")
                    
                    # 단어 가공 및 빈도 측정
                    words = clean_text_and_get_words(comment_data)
                    word_counts = Counter(words)
                    
                    # 🔥 [추가 기능] 가장 많이 사용된 단어 요약 바 시각화
                    if word_counts:
                        st.subheader("💡 핵심 요약: 가장 많이 사용된 단어 Top 5")
                        top_5 = word_counts.most_common(5)
                        
                        # 가로로 깔끔하게 배치
                        cols = st.columns(5)
                        for rank, (word, count) in enumerate(top_5, 1):
                            with cols[rank-1]:
                                st.metric(label=f"{rank}위 단어", value=word, delta=f"{count}회 사용")
                        st.markdown("---")
                    
                    # 레이아웃 분할 (좌측: 워드클라우드, 우측: 빈도수 차트)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("☁️ 한글 워드 클라우드")
                        if words:
                            try:
                                wordcloud = WordCloud(
                                    font_path=FONT_PATH,
                                    background_color="white",
                                    width=800,
                                    height=600,
                                    max_words=100
                                ).generate_from_frequencies(word_counts)
                                
                                fig, ax = plt.subplots(figsize=(10, 8))
                                ax.imshow(wordcloud, interpolation="bilinear")
                                ax.axis("off")
                                st.pyplot(fig)
                            except Exception as e:
                                st.error("워드클라우드 생성 중 폰트 오류가 발생했습니다.")
                        else:
                            st.info("분석할 만한 유의미한 단어가 없습니다.")
                            
                    with col2:
                        st.subheader("📈 주요 키워드 전체 순위 (Top 15)")
                        if word_counts:
                            most_common = word_counts.most_common(15)
                            df_counts = pd.DataFrame(most_common, columns=['단어', '빈도수'])
                            st.bar_chart(df_counts.set_index('단어'))
                            st.dataframe(df_counts, use_container_width=True)
                        else:
                            st.info("데이터가 부족합니다.")
                    
                    # 🔥 [추가 기능] 댓글 원본 보기 리스트에 작성자 이름 매핑
                    with st.expander("💬 수집된 원본 댓글 및 작성자 보기"):
                        for i, (author, content) in enumerate(comment_data, 1):
                            st.markdown(f"**{i}. 유저명: `{author}`**")
                            st.write(content)
                            st.markdown("---")
                else:
                    st.info("수집된 댓글이 없거나 댓글 기능이 비활성화되어 있습니다.")
