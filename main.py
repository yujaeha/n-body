import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 스트림릿 페이지 설정
st.set_page_config(page_title="3D 블랙홀 중력렌즈 시뮬레이션", layout="wide")

st.title("🕳️ 3D 블랙홀 및 중력 렌즈 효과 시뮬레이션")
st.markdown("정중앙에 위치한 거대 블랙홀의 중력에 의해 주변 천체들과 빛의 궤도가 휘어지다가 '사건의 지평선' 속으로 빨려 들어가는 현상을 시뮬레이션합니다.")

# --- 사이드바 설정 (컨트롤러) ---
st.sidebar.header("⚙️ 블랙홀 및 우주 설정")

# 블랙홀 질량 (사건의 지평선 크기에 직결)
M = st.sidebar.slider("블랙홀 질량 (M)", min_value=10.0, max_value=200.0, value=50.0, step=10.0)

# 주변 천체/광자 개수
N = st.sidebar.slider("주변 천체 개수 (N)", min_value=3, max_value=20, value=8, step=1)

# 시간 변화량 (dt)
dt = st.sidebar.slider("시간 걸음 (dt)", min_value=0.01, max_value=0.08, value=0.04, step=0.01)

# 프레임 수
steps = st.sidebar.slider("시뮬레이션 프레임 수", min_value=50, max_value=300, value=150, step=50)

# 슈바르츠실트 반경 (사건의 지평선 크기 계산용 근사치)
# 이 반경 안으로 들어오면 블랙홀에 흡수된 것으로 처리합니다.
rs = 0.04 * M 

# --- 시뮬레이션 상태 관리를 위한 세션 상태 초기화 ---
if 'bh_pos' not in st.session_state or st.sidebar.button("🌌 우주 재구성 (초기화)"):
    # 블랙홀은 항상 (0, 0, 0) 고정
    st.session_state.bh_pos = np.array([0.0, 0.0, 0.0])
    
    # 천체들의 초기 3D 위치 (블랙홀 주변 원형 혹은 무작위 배치)
    # X, Z 축 위주로 넓게 배치하고 Y축으로 약간의 입체감 부여
    positions = np.random.uniform(-12, 12, (N, 3))
    # 지나치게 블랙홀과 가깝게 스폰되는 것 방지
    for i in range(N):
        while np.linalg.norm(positions[i]) < rs + 2.0:
            positions[i] = np.random.uniform(-12, 12, 3)
            
    st.session_state.bh_positions = positions
    
    # 천체들의 초기 속도 (블랙홀 주위를 공전하거나 스쳐 지나가도록 설정)
    # 원 운동에 가까운 속도 벡터를 부여하기 위해 위치 벡터와 직교하는 성분 유도
    velocities = np.zeros((N, 3))
    for i in range(N):
        p = positions[i]
        # 외적을 이용해 직교하는 공전 속도 방향 생성
        v_dir = np.array([-p[2], 0.1, p[0]]) 
        v_dir = v_dir / np.linalg.norm(v_dir)
        # 공전 속도 크기 지정
        v_speed = np.sqrt(M / (np.linalg.norm(p) + 0.1)) * 0.4
        velocities[i] = v_dir * v_speed
        
    st.session_state.bh_velocities = velocities
    # 천체들의 생존 여부 (블랙홀에 흡수되면 False)
    st.session_state.alive = np.ones(N, dtype=bool)
    # 각 천체들의 궤도 기록 배열
    st.session_state.bh_histories = [[positions[i].copy()] for i in range(N)]

# --- 시뮬레이션 시작 버튼 및 루프 ---
if st.button("▶️ 블랙홀 시뮬레이션 가동"):
    plot_spot = st.empty()
    
    for step in range(steps):
        pos = st.session_state.bh_positions
        vel = st.session_state.bh_velocities
        alive = st.session_state.alive
        histories = st.session_state.bh_histories
        
        # 물리 연산 및 위치 업데이트
        for i in range(N):
            if not alive[i]:
                continue
                
            r_vector = -pos[i] # 블랙홀(0,0,0)을 향하는 벡터
            r_distance = np.linalg.norm(r_vector)
            
            # 사건의 지평선(슈바르츠실트 반경) 내부로 진입 시 흡수 처리
            if r_distance <= rs:
                alive[i] = False
                continue
                
            # 뉴턴 중력에 일반상대론적 효과(가까울수록 급격히 강해지는 중력)를 모사한 보정 인자 추가
            # 가속도 a = M / r^2 * (방향 벡터) -> 단위벡터화 적용 시 M * r_vector / r^3
            # 상대론적 효과 보정: 거리가 가까울수록 중력이 기하급수적으로 증가
            relativity_factor = 1.0 + (3.0 * (rs**2) / (r_distance**2 + 0.1))
            acc = (M * relativity_factor / (r_distance**3 + 0.1)) * r_vector
            
            # 속도 및 위치 변경
            vel[i] += acc * dt
            pos[i] += vel[i] * dt
            
            # 궤도 기록 추가
            histories[i].append(pos[i].copy())
            
        # 세션 상태 갱신
        st.session_state.bh_positions = pos
        st.session_state.bh_velocities = vel
        st.session_state.alive = alive
        st.session_state.bh_histories = histories
        
        # --- Plotly 3D 시각화 구현 ---
        fig = go.Figure()
        
        # 1. 중심 거대 블랙홀(사건의 지평선) 그리기
        # 구체 형태를 표현하기 위해 메쉬 그리드 생성
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        x_bh = rs * np.outer(np.cos(u), np.sin(v))
        y_bh = rs * np.outer(np.sin(u), np.sin(v))
        z_bh = rs * np.outer(np.ones(np.size(u)), np.cos(v))
        
        fig.add_trace(go.Surface(
            x=x_bh, y=y_bh, z=z_bh,
            colorscale=[[0, 'rgb(5,5,5)'], [1, 'rgb(15,15,15)']],
            showscale=False,
            opacity=1.0,
            name="사건의 지평선"
        ))
        
        # 빛이 휘는 아인슈타인 링 효과를 시각화하기 위한 가상의 흡수 원반(Accretion Disk) 경계선 추가
        disk_r = np.linspace(rs, rs * 2.5, 10)
        disk_theta = np.linspace(0, 2*np.pi, 30)
        dr, dt_mesh = np.meshgrid(disk_r, disk_theta)
        x_disk = dr * np.cos(dt_mesh)
        y_disk = np.zeros_like(x_disk)
        z_disk = dr * np.sin(dt_mesh)
        
        fig.add_trace(go.Surface(
            x=x_disk, y=y_disk, z=z_disk,
            colorscale='YlOrRd',
            showscale=False,
            opacity=0.3,
            name="강착 원반"
        ))
        
        # 2. 천체들의 이동 궤도(꼬리) 그리기
        for i in range(N):
            if len(histories[i]) > 1:
                h_arr = np.array(histories[i])
                fig.add_trace(go.Scatter3d(
                    x=h_arr[:, 0], y=h_arr[:, 1], z=h_arr[:, 2],
                    mode='lines',
                    line=dict(
                        color='rgba(255, 165, 0, 0.6)' if alive[i] else 'rgba(255, 0, 0, 0.2)', 
                        width=2.5
                    ),
                    showlegend=False
                ))
                
        # 3. 현재 살아있는 천체들의 위치 표시
        alive_indices = np.where(alive == True)[0]
        if len(alive_indices) > 0:
            fig.add_trace(go.Scatter3d(
                x=pos[alive_indices, 0],
                y=pos[alive_indices, 1],
                z=pos[alive_indices, 2],
                mode='markers',
                marker=dict(size=5, color='cyan', opacity=0.9, line=dict(color='white', width=0.5)),
                showlegend=False
            ))
            
        # 레이아웃 구성 및 다크 테마 적용
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
        
        plot_spot.plotly_chart(fig, use_container_width=True, key=f"blackhole_{step}")
        time.sleep(0.01)
        
    # 실시간 생존 수 계산 후 결과 보고
    survivors = np.sum(st.session_state.alive)
    st.success(f"시뮬레이션 종료! 총 {N}개의 천체 중 {N - survivors}개가 블랙홀에 흡수되었고, {survivors}개가 중력권을 탈출하거나 공전 중입니다.")

else:
    # 정지 상태 초기 화면
    fig = go.Figure()
    
    # 초기 블랙홀 모형
    u = np.linspace(0, 2 * np.pi, 15)
    v = np.linspace(0, np.pi, 15)
    x_bh = rs * np.outer(np.cos(u), np.sin(v))
    y_bh = rs * np.outer(np.sin(u), np.sin(v))
    z_bh = rs * np.outer(np.ones(np.size(u)), np.cos(v))
    fig.add_trace(go.Surface(x=x_bh, y=y_bh, z=z_bh, colorscale=[[0, 'black'], [1, 'black']], showscale=False))
    
    # 초기 천체 위치
    pos = st.session_state.bh_positions
    fig.add_trace(go.Scatter3d(x=pos[:, 0], y=pos[:, 1], z=pos[:, 2], mode='markers', marker=dict(size=5, color='cyan')))
    
    fig.update_layout(
        template="plotly_dark", margin=dict(l=0, r=0, b=0, t=0),
        scene=dict(
            xaxis=dict(range=[-15, 15], showgrid=False, showticklabels=False),
            yaxis=dict(range=[-15, 15], showgrid=False, showticklabels=False),
            zaxis=dict(range=[-15, 15], showgrid=False, showticklabels=False),
            aspectmode='cube'
        ),
        width=800, height=700
    )
    st.plotly_chart(fig, use_container_width=True, key="bh_initial")
