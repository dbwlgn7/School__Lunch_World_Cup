import streamlit as st
import random
import uuid
from supabase import create_client, Client

# 페이지 및 테마 설정 (발로란트 챔피언스 2025 밴달 블랙 & 골드 테마)
st.set_page_config(page_title="급식 월드컵", page_icon="🍱", layout="centered")

st.markdown('''
<style>
/* 전체 배경 블랙 */
.stApp {
    background-color: #0f0f0f;
}

/* 텍스트 골드 */
h1, h2, h3, p, div, span {
    color: #d4af37 !important;
    font-family: 'Malgun Gothic', sans-serif;
}

/* 선택 버튼 스타일링 */
div.stButton > button {
    background-color: #1a1a1a;
    color: #d4af37 !important;
    border: 2px solid #d4af37;
    border-radius: 4px;
    padding: 30px;
    font-size: 28px;
    font-weight: 800;
    width: 100%;
    height: 200px;
    transition: 0.2s;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
}

/* 호버 시 테마 효과 */
div.stButton > button:hover {
    background-color: #d4af37;
    color: #0f0f0f !important;
    border: 2px solid #fff200;
    box-shadow: 0 0 20px rgba(255, 242, 0, 0.6);
}

div.stButton > button:active {
    background-color: #b38b22;
}

/* 제목 중앙 정렬 */
.title-text {
    text-align: center;
    font-size: 40px;
    font-weight: 900;
    margin-bottom: 30px;
    text-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
}

.subtitle-text {
    text-align: center;
    font-size: 24px;
    margin-bottom: 20px;
}
</style>
''', unsafe_allow_html=True)

# Supabase 연결 설정
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error("Supabase 연결 설정에 실패했습니다. secrets.toml을 확인해 주세요.")
    st.stop()

# 게임 초기화 함수
def reset_game():
    st.session_state.game_id = str(uuid.uuid4())
    candidates = ['제육볶음', '간장찜닭', '가자미순살튀김', '돈육불백', '미트볼데리야끼볶음', '수육', '진미채고추장볶음', '치즈떡닭갈비']
    random.shuffle(candidates)
    
    # 8강 매치업 생성
    st.session_state.matches = [(candidates[i], candidates[i+1]) for i in range(0, 8, 2)]
    st.session_state.next_round_winners = []
    st.session_state.current_match_idx = 0
    st.session_state.current_round = '8강'
    st.session_state.is_done = False
    st.session_state.winner = None
    st.session_state.locked = False

# 초기 상태 세팅
if 'game_id' not in st.session_state:
    reset_game()

# 메뉴 선택 시 처리 로직
def select_menu(left_menu, right_menu, chosen_menu):
    if st.session_state.locked:
        return
        
    try:
        # Supabase에 대결 결과 저장
        data, count = supabase.table("menu_duels").insert({
            "game_id": st.session_state.game_id,
            "round": st.session_state.current_round,
            "left_menu": left_menu,
            "right_menu": right_menu,
            "winner": chosen_menu
        }).execute()
        
        # 저장 성공 시 다음 단계로 진행
        st.session_state.next_round_winners.append(chosen_menu)
        st.session_state.current_match_idx += 1
        
        # 현재 라운드의 모든 경기가 끝났는지 확인
        if st.session_state.current_match_idx >= len(st.session_state.matches):
            winners = st.session_state.next_round_winners
            if len(winners) == 4:
                st.session_state.current_round = '4강'
                st.session_state.matches = [(winners[0], winners[1]), (winners[2], winners[3])]
            elif len(winners) == 2:
                st.session_state.current_round = '결승'
                st.session_state.matches = [(winners[0], winners[1])]
            elif len(winners) == 1:
                st.session_state.is_done = True
                st.session_state.winner = winners[0]
            
            st.session_state.next_round_winners = []
            st.session_state.current_match_idx = 0
            
    except Exception as e:
        # 저장 실패 시 진행을 잠그고 안내
        st.session_state.locked = True
        st.error(f"결과를 저장하지 못했습니다. 확인이 필요합니다. (오류: {str(e)})")

# 화면 표시
st.markdown("<div class='title-text'>🏆 최애 급식 월드컵 🏆</div>", unsafe_allow_html=True)

if st.session_state.is_done:
    st.markdown(f"<div class='subtitle-text'>🎉 최종 우승: <b>{st.session_state.winner}</b> 🎉</div>", unsafe_allow_html=True)
    if st.button("다시 시작하기", key="restart_btn"):
        reset_game()
        st.rerun()
else:
    if st.session_state.locked:
        st.error("데이터베이스 저장 확인이 필요하여 진행이 잠겼습니다. 새로고침하여 다시 시작해 주세요.")
    else:
        current_match = st.session_state.matches[st.session_state.current_match_idx]
        left_item = current_match[0]
        right_item = current_match[1]
        
        st.markdown(f"<div class='subtitle-text'>🔥 {st.session_state.current_round} ({st.session_state.current_match_idx + 1}/{len(st.session_state.matches)}) 🔥</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(left_item, key=f"left_{st.session_state.current_round}_{st.session_state.current_match_idx}"):
                select_menu(left_item, right_item, left_item)
                st.rerun()
        with col2:
            if st.button(right_item, key=f"right_{st.session_state.current_round}_{st.session_state.current_match_idx}"):
                select_menu(left_item, right_item, right_item)
                st.rerun()
