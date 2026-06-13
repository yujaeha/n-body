import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# 스트림릿 페이지 설정
st.set_page_config(page_title="N-Body 중력 시뮬레이션", layout="wide")

st.title("🌌 N-Body 우주 중력 시뮬레이션")
st.markdown("뉴턴의 만유인력 법칙을 기반으로 여러 천체들이 서로의 중력에 의해 끌려가며 만드는 궤도를 실시간으로 시뮬레이션합니다.")

# --- 사이드바 설정 (컨트롤러) ---
st.sidebar.header("🚀 시뮬레이션 설정")

# 중력 상수 (G)
G = st.sidebar.slider("중력 상수 (G)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)

# 천체의 개수 (N)
N = st.sidebar.slider("천체의 개수 (N)", min_value=2, max_value=20, value=5, step=1)

# 시간 변화량 (dt)
dt = st.sidebar.slider("시간 걸음 (dt)", min_value=0.01, max_value=0.10, value=0.05, step=0.01)

# 소프트닝 인자 (거리가 0이 될 때 힘이 무한대가 되는 것을 방지)
softening = 0.1

# 루프 횟수
steps = st.sidebar.slider("프레임 수", min_value=50, max_value=500, value=200, step=50)

# 시뮬레이션 상태 관리를 위한 세션 상태 초기화
if 'positions' not in st.session_state or st.sidebar.button("🌌 우주 초기화 및 재생성"):
    # 무작위 위치 (X, Y) 생성 (-5에서 5 사이)
    st.session_state.positions = np.random.uniform(-5, 5, (N, 2))
    # 무작위 속도 (Vx, Vy) 생성 (-0.5에서 0.5 사이)
    st.session_state.velocities = np.random.uniform(-0.5, 0.5, (N, 2))
    # 무작위 질량 생성 (10에서 100 사이)
    st.session_state.masses = np.random.uniform(10, 100, (N, 1))
    # 궤도 추적을 위한 기록 리스트
    st.session_state.history = [st.session_state.positions.copy()]

# --- 메인 가속도 계산 함수 (N-Body 핵심 로직) ---
def compute_accelerations(pos, masses, G, softening):
    N = pos.shape[0]
    a = np.zeros((N, 2))
    
    for i in range(N):
        # 다른 모든 천체들과의 거리 벡터 계산
        dx = pos[:, 0] - pos[i, 0]
        dy = pos[:, 1] - pos[i, 1]
        
        # 거리의 제곱 계산 (소프트닝 추가하여 분모가 0이 되는 현상 방지)
        r2 = dx**2 + dy**2 + softening**2
        r3 = np.sqrt(r2)**3
        
        # 가속도 계산: a = G * m * r_vector / r^3
        a[i, 0] = G * np.sum(masses.flatten() * dx / r3)
        a[i, 1] = G * np.sum(masses.flatten() * dy / r3)
        
    return a

# --- 시뮬레이션 실행 버튼 및 애니메이션 화면 ---
if st.button("▶️ 시뮬레이션 시작"):
    # 실시간 업데이트를 위한 비어있는 스트림릿 컨테이너 생성
    plot_spot = st.empty()
    
    # 설정된 스텝만큼 루프 돌며 물리 연산 수행
    for step in range(steps):
        pos = st.session_state.positions
        vel = st.session_state.velocities
        masses = st.session_state.masses
        
        # 1. 가속도 계산
        acc = compute_accelerations(pos, masses, G, softening)
        
        # 2. 속도 업데이트 (v = v + a*dt)
        vel += acc * dt
        
        # 3. 위치 업데이트 (x = x + v*dt)
        pos += vel * dt
        
        # 데이터 세션 저장 및 히스토리 기록
        st.session_state.positions = pos
        st.session_state.velocities = vel
        st.session_state.history.append(pos.copy())
        
        # 4. Matplotlib를 이용한 실시간 그래프 그리기
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_facecolor('#0E1117') # 다크 모드 배경색 설정
        fig.patch.set_facecolor('#0E1117')
        
        # 최근 20프레임의 궤도(꼬리) 그리기
        history_arr = np.array(st.session_state.history[-20:])
        for i in range(N):
            ax.plot(history_arr[:, i, 0], history_arr[:, i, 1], color='cyan', alpha=0.3, linewidth=1)
            
        # 현재 천체들의 위치 찍기 (질량 크기에 비례하여 점 크기 조절)
        sizes = masses.flatten() * 2
        sc = ax.scatter(pos[:, 0], pos[:, 1], s=sizes, c=sizes, cmap='autumn', edgecolors='white', alpha=0.9)
        
        # 축 범위 고정 및 UI 정리
        ax.set_xlim(-15, 15)
        ax.set_ylim(-15, 15)
        ax.axis('off')
        
        # 스트림릿 화면 고침
        plot_spot.pyplot(fig)
        plt.close(fig) # 메모리 해제
        
        # 애니메이션 속도 조절용 프레임 지연
        time.sleep(0.02)
        
    st.success("시뮬레이션이 완료되었습니다! 왼쪽 사이드바에서 다시 초기화하거나 설정을 바꿀 수 있습니다.")
else:
    # 최초 진입 시 정지 상태 화면 표시
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor('#0E1117')
    fig.patch.set_facecolor('#0E1117')
    
    pos = st.session_state.positions
    sizes = st.session_state.masses.flatten() * 2
    ax.scatter(pos[:, 0], pos[:, 1], s=sizes, c=sizes, cmap='autumn', edgecolors='white')
    
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.axis('off')
    st.pyplot(fig)
