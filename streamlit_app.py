import streamlit as st
import random
import time

# --- 게임 설정 ---
SCREEN_WIDTH = 15  # 게임 화면의 너비
GROUND_LEVEL = 0   # 땅의 높이
JUMP_HEIGHT = 2    # 점프 최고 높이 (장애물이 1의 높이에 있으므로, 2로 설정)

# --- 게임 상태 초기화 함수 ---
def initialize_game():
    """게임 상태를 초기화하고 세션 상태에 저장합니다."""
    # '다시하기' 버튼을 누르거나 처음 시작할 때만 상태를 초기화합니다.
    if 'initialized' not in st.session_state or st.session_state.get('restart', False):
        st.session_state.player_y = GROUND_LEVEL  # 플레이어의 Y 좌표
        st.session_state.is_jumping = False       # 점프 상태 여부
        st.session_state.is_sliding = False       # 슬라이드 상태 여부
        st.session_state.slide_end_time = 0       # 슬라이드 종료 시간
        st.session_state.obstacles = []           # 장애물 리스트
        st.session_state.score = 0                # 점수
        st.session_state.game_over = False        # 게임 오버 상태
        st.session_state.last_obstacle_spawn_time = time.time() # 마지막 장애물 생성 시간
        st.session_state.restart = False
        st.session_state.initialized = True


# --- 게임 화면 렌더링 함수 ---
def render_game():
    """현재 게임 상태를 기반으로 화면을 그립니다."""
    # 게임 보드 초기화 (3칸 높이)
    board = [["&nbsp;"] * SCREEN_WIDTH for _ in range(JUMP_HEIGHT + 2)]

    # 바닥 그리기
    for i in range(SCREEN_WIDTH):
        board[GROUND_LEVEL][i] = "🟫"

    # 장애물 그리기
    for ob in st.session_state.obstacles:
        # 장애물이 화면 범위 내에 있을 때만 그립니다.
        if 0 <= ob['x'] < SCREEN_WIDTH:
            board[ob['y']][ob['x']] = ob['char']

    # 플레이어(쿠키) 그리기
    # 슬라이드 중이면 엎드린 모양(🙇), 아니면 기본 쿠키(🍪) 모양
    player_char = "🙇" if st.session_state.is_sliding else "🍪"
    player_y_pos = min(JUMP_HEIGHT + 1, max(GROUND_LEVEL, st.session_state.player_y))
    board[player_y_pos][1] = player_char # 플레이어는 1번 x좌표에 고정

    # 보드를 HTML로 변환하여 큰 글씨로 출력
    st.markdown(
        f"""
        <div style="font-size: 24px; line-height: 1.2; font-family: monospace;">
        {'<br>'.join([''.join(row) for row in reversed(board)])}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f"**점수: {st.session_state.score}**")


# --- 메인 게임 로직 ---
st.title("쿠키런: 마녀의 오븐 탈출")

# 게임 시작 버튼
if not st.session_state.get('game_started', False):
    if st.button("시작"):
        st.session_state.game_started = True
        initialize_game()
        st.rerun()
    st.stop()

# 게임 상태 초기화 (시작 또는 다시하기 시)
initialize_game()

# 게임 오버 화면
if st.session_state.game_over:
    st.error("게임 오버! 장애물에 부딪혔습니다.")
    if st.button("다시하기"):
        st.session_state.restart = True
        st.session_state.game_over = False
        st.rerun()
    st.stop()

# 게임 컨트롤 버튼 (점프, 슬라이드)
col1, col2 = st.columns(2)
with col1:
    if st.button("점프", use_container_width=True):
        # 플레이어가 땅에 있고, 점프 중이 아닐 때만 점프 가능
        if not st.session_state.is_jumping and st.session_state.player_y == GROUND_LEVEL:
            st.session_state.is_jumping = True

with col2:
    if st.button("슬라이드", use_container_width=True):
        # 플레이어가 땅에 있고, 슬라이드 중이 아닐 때만 슬라이드 가능
        if not st.session_state.is_sliding and st.session_state.player_y == GROUND_LEVEL:
            st.session_state.is_sliding = True
            # 슬라이드는 0.5초 동안 지속됨
            st.session_state.slide_end_time = time.time() + 0.5

# 게임 화면을 업데이트하기 위한 플레이스홀더
game_placeholder = st.empty()
frame_rate = 0.15  # 게임 속도 (프레임 간 지연 시간)

# --- 메인 게임 루프 ---
while not st.session_state.game_over:

    # 슬라이드 상태 관리
    if st.session_state.is_sliding and time.time() > st.session_state.slide_end_time:
        st.session_state.is_sliding = False

    # 점프 로직 처리
    if st.session_state.is_jumping:
        # 점프 상승
        st.session_state.player_y += 1
        # 최고 높이에 도달하면 점프 상태 종료 (하강 시작)
        if st.session_state.player_y >= JUMP_HEIGHT:
            st.session_state.is_jumping = False
    # 중력 적용 (점프 중이 아니고, 공중에 떠 있을 때)
    elif st.session_state.player_y > GROUND_LEVEL:
        st.session_state.player_y -= 1

    # --- 장애물 생성 로직 (수정됨) ---
    spawn_interval = random.uniform(1.0, 2.5) # 장애물 생성 간격
    if time.time() - st.session_state.last_obstacle_spawn_time > spawn_interval:
        # 50% 확률로 점프 장애물 또는 슬라이드 장애물 생성
        if random.choice([True, False]):
            # 아래쪽 장애물 (점프로 회피)
            new_obstacle = {'x': SCREEN_WIDTH - 1, 'y': GROUND_LEVEL, 'char': '🔥'}
        else:
            # 위쪽 장애물 (슬라이드로 회피)
            new_obstacle = {'x': SCREEN_WIDTH - 1, 'y': GROUND_LEVEL + 1, 'char': '🦅'}
        st.session_state.obstacles.append(new_obstacle)
        st.session_state.last_obstacle_spawn_time = time.time()

    # 장애물 이동 및 점수 획득
    new_obstacles = []
    for ob in st.session_state.obstacles:
        ob['x'] -= 1
        if ob['x'] < 0: # 화면을 벗어난 장애물은 점수 획득 후 제거
            st.session_state.score += 10
        else:
            new_obstacles.append(ob)
    st.session_state.obstacles = new_obstacles

    # --- 충돌 감지 로직 (수정됨) ---
    player_x_pos = 1
    for ob in st.session_state.obstacles:
        if ob['x'] == player_x_pos: # 장애물과 플레이어의 x좌표가 같을 때
            # 1. 위쪽 장애물(🦅)과 충돌: 슬라이드 중이 아닐 때, 플레이어와 장애물 높이가 같으면 충돌
            if ob['char'] == '🦅' and not st.session_state.is_sliding and st.session_state.player_y == ob['y']:
                st.session_state.game_over = True
                break
            # 2. 아래쪽 장애물(🔥)과 충돌: 플레이어가 땅에 있고, 장애물도 땅에 있으면 충돌
            if ob['char'] == '🔥' and st.session_state.player_y == GROUND_LEVEL:
                st.session_state.game_over = True
                break

    # 게임 화면 업데이트
    with game_placeholder.container():
        render_game()

    # 게임 오버 시 루프 탈출 및 재실행
    if st.session_state.game_over:
        st.rerun()

    # 프레임 속도 조절
    time.sleep(frame_rate)