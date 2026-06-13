import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 스트림릿 페이지 설정
st.set_page_config(page_title="3D N-Body 중력 시뮬레이션", layout="wide")

st.title("🌌 3D N-Body 우주 중력 시뮬레이션")
st.markdown("뉴턴의 만유인력 법칙을 3차원 공간(X, Y, Z)으로 확장하여, 마우스로 회전하고 확대하며 관찰할 수 있는 입체 궤도 시뮬레이션입니다.")

# --- 사이드바 설정 (컨트롤러) ---
st.sidebar.header("🚀 시뮬레이션 설정")

G = st.sidebar.slider("중력 상수 (G)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
N = st.sidebar.slider("천체의 개수 (N)", min_value=2, max_value=15, value=5, step=1) # 3D 연산 속도를 고려해 최대치 소폭 조정
dt = st.sidebar.slider("시간 걸음 (dt)", min_value=0.01, max_value=0.10, value=0.05, step=0.01)
steps = st.sidebar.slider("프레임 수", min_value=50, max_value=300, value=150, step=50)

softening = 0.1 # 중력 폭주 방지 인자

# 시뮬레이션 상태 관리를 위한 세션 상태 초기화 (3차원 배열 형태로 변경)
if 'positions_3d' not in st.session_state or st.sidebar.button("🌌 3D 우주 초기화 및 재생성"):
    # 무작위 3차원 위치 (X, Y, Z) 생성 (-5에서 5 사이)
    st.session_state.positions_3d = np.random.uniform(-5, 5, (N, 3))
    # 무작위 3차원 속도 (Vx, Vy, Vz) 생성 (-0.5에서 0.5 사이)
    st.session_state.velocities_3d = np.random.uniform(-0.5, 0.5, (N, 3))
    # 무작위 질량 생성
    st.session_state.masses_3d = np.random.uniform(10, 100, (N, 1))
    # 궤도 추적을 위한 기록 리스트
    st.session_state.history_3d = [st.session_state.positions_3d.copy()]

# --- 3차원 가속도 계산 함수 ---
def compute_accelerations_3d(pos, masses, G, softening):
    N = pos.shape[0]
    a = np.zeros((N, 3)) # X, Y, Z 3가지 축
    
    for i in range(N):
        # 다른 모든 천체들과의 3차원 거리 벡터 계산
        dx = pos[:, 0] - pos[i, 0]
        dy = pos[:, 1] - pos[i, 1]
        dz = pos[:, 2] - pos[i, 2]
        
        # 3차원 공간에서의 거리 제곱 계산
        r2 = dx**2 + dy**2 + dz**2 + softening**2
        r3 = np.sqrt(r2)**3
        
        # 각 축의 가속도 계산
        a[i, 0] = G * np.sum(masses.flatten() * dx / r3)
        a[i, 1] = G * np.sum(masses.flatten() * dy / r3)
        a[i, 2] = G * np.sum(masses.flatten() * dz / r3)
        
    return a

# --- 시뮬레이션 실행 버튼 및 애니메이션 화면 ---
if st.button("▶️ 3D 시뮬레이션 시작"):
    plot_spot = st.empty()
    
    for step in range(steps):
        pos = st.session_state.positions_3d
        vel = st.session_state.velocities_3d
        masses = st.session_state.masses_3d
        
        # 1. 3D 가속도 계산
        acc = compute_accelerations_3d(pos, masses, G, softening)
        
        # 2. 속도 및 위치 업데이트
        vel += acc * dt
        pos += vel * dt
        
        st.session_state.positions_3d = pos
        st.session_state.velocities_3d = vel
        st.session_state.history_3d.append(pos.copy())
        
        # 3. Plotly를 이용한 대화형 3D 그래프 생성
        fig = go.Figure()
        
        # 최근 25프레임의 3D 궤도(꼬리) 그리기
        history_arr = np.array(st.session_state.history_3d[-25:])
        for i in range(N):
            fig.add_trace(go.Scatter3d(
                x=history_arr[:, i, 0],
                y=history_arr[:, i, 1],
                z=history_arr[:, i, 2],
                mode='lines',
                line=dict(color='cyan', width=2),
                opacity=0.4,
                showlegend=False
            ))
            
        # 현재 천체들의 3D 위치 찍기
        sizes = masses.flatten() * 0.3 # Plotly 크기 규격에 맞게 조정
        fig.add_trace(go.Scatter3d(
            x=pos[:, 0],
            y=pos[:, 1],
            z=pos[:, 2],
            mode='markers',
            marker=dict(
                size=sizes,
                color=sizes,
                colorscale='Inferno',
                line=dict(color='white', width=1),
                opacity=0.9
            ),
            showlegend=False
        ))
        
        # 3D 우주 배경 및 레이아웃 설정
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(
                xaxis=dict(range=[-15, 15], backgroundcolor="rgb(14, 17, 23)", showgrid=False, showticklabels=False, title=''),
                yaxis=dict(range=[-15, 15], backgroundcolor="rgb(14, 17, 23)", showgrid=False, showticklabels=False, title=''),
                zaxis=dict(range=[-15, 15], backgroundcolor="rgb(14, 17, 23)", showgrid=False, showticklabels=False, title=''),
                aspectmode='cube'
            ),
            width=800,
            height=700
        )
        
        # 스트림릿 화면 고침 (Plotly 전용 함수 사용)
        plot_spot.plotly_chart(fig, use_container_width=True, key=f"plotly_step_{step}")
        
        # 애니메이션 속도 제어
        time.sleep(0.01)
        
    st.success("3D 시뮬레이션 완료! 마우스로 화면을 드래그하여 다른 각도에서 궤도를 확인해보세요.")
else:
    # 정지 상태 기본 화면
    fig = go.Figure()
    pos = st.session_state.positions_3d
    sizes = st.session_state.masses_3d.flatten() * 0.3
    
    fig.add_trace(go.Scatter3d(
        x=pos[:, 0], y=pos[:, 1], z=pos[:, 2],
        mode='markers',
        marker=dict(size=sizes, color=sizes, colorscale='Inferno', line=dict(color='white', width=1))
    ))
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(range=[-15, 15], showgrid=False, showticklabels=False, title=''),
            yaxis=dict(range=[-15, 15], showgrid=False, showticklabels=False, title=''),
            zaxis=dict(range=[-15, 15], showgrid=False, showticklabels=False, title=''),
            aspectmode='cube'
        ),
        width=800,
        height=700
    )
    st.plotly_chart(fig, use_container_width=True, key="plotly_initial")
