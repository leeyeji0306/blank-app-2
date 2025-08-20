import streamlit as st
from streamlit_keyup import st_keyup
import random
import time

# --- 게임 설정 ---
SCREEN_WIDTH = 15
GROUND_LEVEL = 0
JUMP_HEIGHT = 2

# --- 게임 상태 초기화 함수 ---
def initialize_game_state():
    """게임의 모든 상태를 초기화하고 세션 상태에 저장합니다."""
    # 페이지 상태 (어떤 화면을 보여줄지 결정)
    if 'page' not in st.session_state:
        st.session_state.page = "start" # 시작: start, 키설정: settings, 게임중: game

    # 키 설정 (기본값: 위쪽 화살표, 아래쪽 화살표)
    if 'jump_key' not in st.session_state:
        st.session_state.jump_key = "ArrowUp"
    if 'slide_key' not in st.session_state:
        st.session_state.slide_key = "ArrowDown"

    # 게임 로직 변수
    st.session_state.player_y = GROUND_LEVEL
    st.session_state.is_jumping = False
    st.session_state.is_sliding = False
    st.session_state.slide_end_time = 0
    st.session_state.obstacles = []
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.last_obstacle_spawn_time = time.time()


# --- 화면 렌더링 함수 ---
def render_game_screen():
    """현재 게임 상태를 기반으로 화면을 그립니다."""
    board = [["&nbsp;"] * SCREEN_WIDTH for _ in range(JUMP_HEIGHT + 2)]
    for i in range(SCREEN_WIDTH):
        board[GROUND_LEVEL][i] = "🟫"
    for ob in st.session_state.obstacles:
        if 0 <= ob['x'] < SCREEN_WIDTH:
            board[ob['y']][ob['x']] = ob['char']

    player_char = "🙇" if st.session_state.is_sliding else "🍪"
    player_y_pos = min(JUMP_HEIGHT + 1, max(GROUND_LEVEL, st.session_state.player_y))
    board[player_y_pos][1] = player_char

    st.markdown(
        f"""
        <div style="font-size: 24px; line-height: 1.2; font-family: monospace;">
        {'<br>'.join([''.join(row) for row in reversed(board)])}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f"**점수: {st.session_state.score}**")
    st.info(f"점프: `{st.session_state.jump_key}` / 슬라이드: `{st.session_state.slide_key}`")


# --- 페이지 라우팅 및 관리 ---
st.title("쿠키런: 마녀의 오븐 탈출")

# 세션 상태 초기화 (페이지가 로드될 때 한 번만 실행)
if 'page' not in st.session_state:
    initialize_game_state()

# 1. 시작 화면
if st.session_state.page == "start":
    st.subheader("마녀의 오븐에서 탈출하세요!")
    if st.button("게임 시작", use_container_width=True):
        st.session_state.page = "game"
        initialize_game_state() # 게임 상태 초기화
        st.rerun()

    if st.button("키 설정", use_container_width=True):
        st.session_state.page = "settings"
        st.rerun()

# 2. 키 설정 화면
elif st.session_state.page == "settings":
    st.subheader("키 설정")
    st.write("아래 입력창을 클릭하고 원하는 키를 누르세요.")

    # st_keyup을 사용하여 사용자 입력 키를 받음
    new_jump_key = st_keyup("점프 키 설정", value=st.session_state.jump_key, key="jump_key_input")
    if new_jump_key:
        st.session_state.jump_key = new_jump_key

    new_slide_key = st_keyup("슬라이드 키 설정", value=st.session_state.slide_key, key="slide_key_input")
    if new_slide_key:
        st.session_state.slide_key = new_slide_key

    st.success(f"점프 키: `{st.session_state.jump_key}` / 슬라이드 키: `{st.session_state.slide_key}` 로 설정되었습니다.")

    if st.button("뒤로가기"):
        st.session_state.page = "start"
        st.rerun()

# 3. 게임 플레이 화면
elif st.session_state.page == "game":
    # 게임 오버 시
    if st.session_state.game_over:
        st.error("게임 오버! 장애물에 부딪혔습니다.")
        if st.button("다시하기", use_container_width=True):
            initialize_game_state()
            st.session_state.page = "game" # 페이지 상태 유지
            st.rerun()
        if st.button("시작 화면으로", use_container_width=True):
            st.session_state.page = "start"
            st.rerun()
        st.stop()

    # --- 키보드 입력 처리 ---
    # 빈 공간에 st_keyup을 보이지 않게 배치하여 키 입력을 계속 감지
    key_pressed = st_keyup(" ", debounce=50, key="key_game_input")

    if key_pressed:
        # 점프 키 처리
        if key_pressed == st.session_state.jump_key:
            if not st.session_state.is_jumping and st.session_state.player_y == GROUND_LEVEL:
                st.session_state.is_jumping = True
        # 슬라이드 키 처리
        elif key_pressed == st.session_state.slide_key:
            if not st.session_state.is_sliding and st.session_state.player_y == GROUND_LEVEL:
                st.session_state.is_sliding = True
                st.session_state.slide_end_time = time.time() + 0.5

    # --- 게임 로직 (이전과 동일) ---
    game_placeholder = st.empty()
    frame_rate = 0.15

    while not st.session_state.game_over:
        if st.session_state.is_sliding and time.time() > st.session_state.slide_end_time:
            st.session_state.is_sliding = False

        if st.session_state.is_jumping:
            st.session_state.player_y += 1
            if st.session_state.player_y >= JUMP_HEIGHT:
                st.session_state.is_jumping = False
        elif st.session_state.player_y > GROUND_LEVEL:
            st.session_state.player_y -= 1

        spawn_interval = random.uniform(1.0, 2.5)
        if time.time() - st.session_state.last_obstacle_spawn_time > spawn_interval:
            if random.choice([True, False]):
                new_obstacle = {'x': SCREEN_WIDTH - 1, 'y': GROUND_LEVEL, 'char': '🔥'}
            else:
                new_obstacle = {'x': SCREEN_WIDTH - 1, 'y': GROUND_LEVEL + 1, 'char': '🦅'}
            st.session_state.obstacles.append(new_obstacle)
            st.session_state.last_obstacle_spawn_time = time.time()

        new_obstacles = []
        for ob in st.session_state.obstacles:
            ob['x'] -= 1
            if ob['x'] < 0:
                st.session_state.score += 10
            else:
                new_obstacles.append(ob)
        st.session_state.obstacles = new_obstacles

        player_x_pos = 1
        for ob in st.session_state.obstacles:
            if ob['x'] == player_x_pos:
                if ob['char'] == '🦅' and not st.session_state.is_sliding and st.session_state.player_y == ob['y']:
                    st.session_state.game_over = True
                    break
                if ob['char'] == '🔥' and st.session_state.player_y == GROUND_LEVEL:
                    st.session_state.game_over = True
                    break

        with game_placeholder.container():
            render_game_screen()

        if st.session_state.game_over:
            st.rerun()

        time.sleep(frame_rate)
        # 게임 루프 중에는 키 입력을 받기 위해 페이지를 계속 재실행
        st.rerun()