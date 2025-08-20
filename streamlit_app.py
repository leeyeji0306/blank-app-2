import streamlit as st
import random
import time

# --- 게임 설정 ---
SCREEN_WIDTH = 15  # 게임 화면의 너비
GROUND_LEVEL = 0   # 땅의 높이
JUMP_HEIGHT = 3    # 점프 최고 높이
GRAVITY = 1        # 중력 값

# --- 게임 상태 초기화 함수 ---
def initialize_game():
    """게임 상태를 초기화하고 세션 상태에 저장합니다."""
    if 'initialized' not in st.session_state or st.session_state.get('restart', False):
        st.session_state.player_y = GROUND_LEVEL  # 플레이어의 Y 좌표
        st.session_state.player_velocity = 0      # 플레이어의 수직 속도
        st.session_state.is_jumping = False       # 점프 상태 여부
        st.session_state.is_sliding = False       # 슬라이드 상태 여부
        st.session_state.obstacles = []           # 장애물 리스트
        st.session_state.score = 0                # 점수
        st.session_state.game_over = False        # 게임 오버 상태
        st.session_state.last_obstacle_spawn_time = time.time() # 마지막 장애물 생성 시간
        st.session_state.restart = False
        st.session_state.initialized = True


# --- 게임 화면 렌더링 함수 ---
def render_game():
    """현재 게임 상태를 기반으로 화면을 그립니다."""
    # 게임 보드 초기화 (빈 공간으로 채움)
    board = [["&nbsp;"] * SCREEN_WIDTH for _ in range(JUMP_HEIGHT + 1)]

    # 바닥 그리기
    for i in range(SCREEN_WIDTH):
        board[GROUND_LEVEL][i] = "🟫"

    # 장애물 그리기
    for ob in st.session_state.obstacles:
        if 0 <= ob['x'] < SCREEN_WIDTH:
            board[ob['y']][ob['x']] = ob['char']

    # 플레이어(쿠키) 그리기
    player_char = "🙇" if st.session_state.is_sliding else "🍪"
    # 플레이어 위치가 화면 범위 내에 있는지 확인
    player_y_pos = min(JUMP_HEIGHT, max(GROUND_LEVEL, st.session_state.player_y))
    board[player_y_pos][1] = player_char

    # 보드를 문자열로 변환하여 출력
    # 스타일을 적용하여 폰트 크기를 키우고 줄 간격을 조절합니다.
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

# 게임이 시작되지 않았을 때 '시작' 버튼 표시
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if not st.session_state.game_started:
    if st.button("시작"):
        st.session_state.game_started = True
        initialize_game()
        st.rerun() # 버튼을 누르면 즉시 게임을 시작하기 위해 재실행
    st.stop() # 게임이 시작되지 않았으면 여기서 실행 중지

# 게임 상태 초기화
initialize_game()

# 게임 오버 시 '다시하기' 버튼 표시
if st.session_state.game_over:
    st.error("게임 오버! 장애물에 부딪혔습니다.")
    if st.button("다시하기"):
        st.session_state.restart = True
        st.session_state.game_over = False
        st.session_state.game_started = True # 다시 시작할 때도 게임 상태 유지
        st.rerun() # 재시작
    st.stop() # 게임이 오버되면 여기서 실행 중지

# 게임 컨트롤 버튼 (두 개의 컬럼으로 배치)
col1, col2 = st.columns(2)
with col1:
    if st.button("점프", use_container_width=True):
        if not st.session_state.is_jumping:
            st.session_state.is_jumping = True
            st.session_state.player_velocity = JUMP_HEIGHT # 점프 시작 시 속도 설정

with col2:
    # 슬라이드 버튼은 누르고 있을 때만 활성화되도록 구현
    if 'slide_button' not in st.session_state:
        st.session_state.slide_button = False

    if st.button("슬라이드", use_container_width=True):
       # 슬라이드 로직을 여기에 간단히 구현할 수 있습니다.
       # 여기서는 시각적 변화만 주겠습니다.
       st.session_state.is_sliding = True
    else:
       st.session_state.is_sliding = False


# 게임 화면을 위한 플레이스홀더
game_placeholder = st.empty()
frame_rate = 0.2 # 게임 속도 조절

# --- 게임 루프 ---
while not st.session_state.game_over:
    # 점프 로직 처리
    if st.session_state.is_jumping:
        st.session_state.player_y += 1  # 점프 시 y 좌표 증가
        # 최고 높이에 도달하면 하강 시작
        if st.session_state.player_y >= JUMP_HEIGHT:
            st.session_state.is_jumping = False
    # 중력 적용 (점프 중이 아닐 때)
    elif st.session_state.player_y > GROUND_LEVEL:
        st.session_state.player_y -= st.session_state.player_velocity
        st.session_state.player_y = max(GROUND_LEVEL, st.session_state.player_y)

    # 장애물 생성 로직
    # 1.5초에서 3초 사이의 랜덤한 간격으로 장애물 생성
    spawn_interval = random.uniform(1.5, 3.0)
    if time.time() - st.session_state.last_obstacle_spawn_time > spawn_interval:
        new_obstacle = {'x': SCREEN_WIDTH - 1, 'y': GROUND_LEVEL, 'char': '🔥'}
        st.session_state.obstacles.append(new_obstacle)
        st.session_state.last_obstacle_spawn_time = time.time()


    # 장애물 이동 및 점수 획득
    new_obstacles = []
    for ob in st.session_state.obstacles:
        ob['x'] -= 1 # 왼쪽으로 한 칸 이동
        if ob['x'] < 0: # 화면을 벗어난 장애물
            st.session_state.score += 10 # 장애물 통과 시 점수 획득
        else:
            new_obstacles.append(ob)
    st.session_state.obstacles = new_obstacles

    # 충돌 감지
    for ob in st.session_state.obstacles:
        # 플레이어 x좌표는 1로 고정
        # 슬라이드 상태가 아닐 때만 충돌 감지 (슬라이드는 장애물을 피하는 것으로 가정)
        if ob['x'] == 1 and st.session_state.player_y == ob['y'] and not st.session_state.is_sliding:
            st.session_state.game_over = True
            break

    # 게임 화면 업데이트
    with game_placeholder.container():
        render_game()

    # 게임 루프 중단 조건
    if st.session_state.game_over:
        st.rerun() # 게임 오버 화면을 즉시 표시하기 위해 재실행

    # 프레임 속도 조절
    time.sleep(frame_rate)