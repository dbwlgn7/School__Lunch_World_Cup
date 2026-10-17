import streamlit as st
import random
import uuid
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# 페이지 및 테마 설정
st.set_page_config(page_title="급식 월드컵", page_icon="🍱", layout="centered")

# 챔피언스 밴달 테마 CSS (3D 입체감, 금빛 네온, 다크 카본 느낌, 정렬 개선)
st.markdown('''
<style>
/* 전체 배경: 어두운 카본 느낌의 블랙 */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1a1a24 0%, #0a0a0f 80%);
    color: #e0e0e0;
}

/* 텍스트 색상 및 폰트 */
h1, h2, h3, h4, h5, p, div, span {
    font-family: 'Malgun Gothic', sans-serif;
}

/* 황금색 하이라이트 텍스트 */
.gold-text {
    color: #d4af37;
    text-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
    font-weight: 900;
}

/* 제목 중앙 정렬 및 챔피언스 스타일 */
.title-text {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    margin-bottom: 5px;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: 2px;
    text-shadow: 0 0 15px #d4af37, 0 0 30px #d4af37;
}

.subtitle-text {
    text-align: center;
    font-size: 22px;
    margin-bottom: 40px;
    color: #a0a0a0;
}

/* 🏆 선택 버튼 컨테이너 (정렬 개선) */
.menu-card {
    background: #111;
    border: 1px solid #222;
    border-radius: 12px;
    padding: 20px 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    text-align: center;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* 이모티콘 텍스트 스타일 */
.emoji-icon {
    font-size: 80px;
    margin-bottom: 15px;
    text-shadow: 0 5px 15px rgba(0,0,0,0.5);
    line-height: 1;
}

/* 선택 버튼 3D 스타일링 (밴달의 날카롭고 입체적인 느낌) */
div.stButton > button {
    background: linear-gradient(135deg, #181818 0%, #2a2a2a 100%);
    color: #d4af37 !important;
    border: 1px solid #333;
    border-top: 2px solid #d4af37;
    border-radius: 8px;
    padding: 15px;
    font-size: 20px;
    font-weight: 800;
    width: 100%;
    height: auto;
    min-height: 60px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 10px 20px rgba(0,0,0,0.5), inset 0 2px 5px rgba(255,255,255,0.1);
    white-space: normal;
    word-break: keep-all;
}

/* 호버 시 챔피언스 오라 이펙트 */
div.stButton > button:hover {
    background: linear-gradient(135deg, #d4af37 0%, #b38b22 100%);
    color: #000 !important;
    border: 1px solid #fff200;
    box-shadow: 0 15px 25px rgba(212, 175, 55, 0.4), inset 0 2px 10px rgba(255,255,255,0.5);
    transform: translateY(-5px);
}

div.stButton > button:active {
    transform: translateY(2px);
    box-shadow: 0 5px 10px rgba(0,0,0,0.5);
}

/* 챔피언스 빛나는 박스 */
.glow-box {
    background: rgba(20, 20, 20, 0.8);
    border-left: 4px solid #d4af37;
    padding: 20px;
    border-radius: 5px;
    margin-bottom: 20px;
}
</style>
''', unsafe_allow_html=True)

# 후보 및 이모티콘 맵
CANDIDATES = ['제육볶음', '간장찜닭', '가자미순살튀김', '돈육불백', '미트볼데리야끼볶음', '수육', '진미채고추장볶음', '치즈떡닭갈비']
EMOJI_MAP = {
    '제육볶음': '🔥🐷',
    '간장찜닭': '🍗🤎',
    '가자미순살튀김': '🐟🍤',
    '돈육불백': '🍖🧅',
    '미트볼데리야끼볶음': '🧆✨',
    '수육': '🥓🥬',
    '진미채고추장볶음': '🦑🌶️',
    '치즈떡닭갈비': '🧀🥘'
}

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

# 통계 분석 및 화면 표시 함수
def show_analytics():
    st.markdown("<h2 class='gold-text' style='text-align: center; margin-top: 50px;'>📊 학급 전체 대결 기록 분석</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 최신 결과 불러오기", key="refresh_stats"):
            pass 
            
    try:
        response = supabase.table("menu_duels").select("id, game_id, round, left_menu, right_menu, winner").execute()
        data = response.data
        
        if not data:
            st.info("아직 저장된 대결 기록이 없습니다.")
            return
            
        df = pd.DataFrame(data)
        total_records = len(df)
        total_games = df['game_id'].nunique()
        
        st.markdown(f'''
        <div class="glow-box">
            <p>📌 <b>집계 기준:</b> 총 <b>{total_records}</b>건의 대결 기록 (총 <b>{total_games}</b>판)</p>
            <p style="font-size: 14px; color: #888;">* 기록 수와 참여 인원은 다르며, 게임을 끝까지 마치지 않고 진행 중에 남긴 대결 결과도 모두 집계에 포함됩니다.</p>
        </div>
        ''', unsafe_allow_html=True)
        
        stats = {menu: {'대결 수': 0, '승리 수': 0, '우승 횟수': 0} for menu in CANDIDATES}
        
        for _, row in df.iterrows():
            l_menu = row['left_menu']
            r_menu = row['right_menu']
            win = row['winner']
            rnd = row['round']
            
            if l_menu in stats: stats[l_menu]['대결 수'] += 1
            if r_menu in stats: stats[r_menu]['대결 수'] += 1
            if win in stats:
                stats[win]['승리 수'] += 1
                if rnd == '결승':
                    stats[win]['우승 횟수'] += 1
                    
        stats_df = pd.DataFrame.from_dict(stats, orient='index').reset_index()
        stats_df.rename(columns={'index': '반찬 이름'}, inplace=True)
        
        stats_df['승률(%)_raw'] = stats_df.apply(lambda r: (r['승리 수'] / r['대결 수'] * 100) if r['대결 수'] > 0 else -1, axis=1)
        stats_df['승률'] = stats_df.apply(lambda r: f"{r['승리 수']/r['대결 수']*100:.1f}%" if r['대결 수'] > 0 else '아직 알 수 없음', axis=1)
        
        stats_df = stats_df.sort_values(by=['승률(%)_raw', '우승 횟수', '승리 수'], ascending=[False, False, False])
        
        display_df = stats_df[['반찬 이름', '대결 수', '승리 수', '승률', '우승 횟수']].copy()
        display_df.index = range(1, len(display_df) + 1)
        
        st.dataframe(display_df, use_container_width=True)
        
        plot_df = stats_df[stats_df['승률(%)_raw'] >= 0].copy()
        if not plot_df.empty:
            plot_df = plot_df.sort_values(by='승률(%)_raw', ascending=True)
            fig = px.bar(
                plot_df, x='승률(%)_raw', y='반찬 이름', orientation='h',
                title="🏆 반찬별 승률 비교",
                labels={'승률(%)_raw': '승률 (%)', '반찬 이름': ''},
                color='승률(%)_raw',
                color_continuous_scale=['#333333', '#d4af37']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0'),
                title_font=dict(color='#d4af37', size=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"통계 데이터를 조회하는 중 오류가 발생했습니다: {str(e)}")


# 게임 초기화
def reset_game():
    st.session_state.game_id = str(uuid.uuid4())
    candidates = CANDIDATES.copy()
    random.shuffle(candidates)
    
    st.session_state.matches = [(candidates[i], candidates[i+1]) for i in range(0, 8, 2)]
    st.session_state.next_round_winners = []
    st.session_state.current_match_idx = 0
    st.session_state.current_round = '8강'
    st.session_state.is_done = False
    st.session_state.winner = None
    st.session_state.locked = False

if 'game_id' not in st.session_state:
    reset_game()

# 메뉴 선택
def select_menu(left_menu, right_menu, chosen_menu):
    if st.session_state.locked:
        return
        
    try:
        data, count = supabase.table("menu_duels").insert({
            "game_id": st.session_state.game_id,
            "round": st.session_state.current_round,
            "left_menu": left_menu,
            "right_menu": right_menu,
            "winner": chosen_menu
        }).execute()
        
        st.session_state.next_round_winners.append(chosen_menu)
        st.session_state.current_match_idx += 1
        
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
        st.session_state.locked = True
        st.error(f"결과를 저장하지 못했습니다. 확인이 필요합니다. (오류: {str(e)})")


# ---------------- UI 화면 표시 ----------------
st.markdown("<div class='title-text'>최애 급식 월드컵</div>", unsafe_allow_html=True)

if st.session_state.is_done:
    st.markdown(f"<div class='subtitle-text'>🎉 <b>최종 우승: <span class='gold-text'>{st.session_state.winner}</span></b> 🎉</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'''
        <div class='menu-card'>
            <div class='emoji-icon'>{EMOJI_MAP.get(st.session_state.winner)}</div>
        </div>
        <br>
        ''', unsafe_allow_html=True)
        if st.button("다시 시작하기", key="restart_btn_end"):
            reset_game()
            st.rerun()
            
    st.markdown("---")
    show_analytics()
    
else:
    if st.session_state.locked:
        st.error("데이터베이스 저장 확인이 필요하여 진행이 잠겼습니다. 오류를 확인해 주세요.")
    else:
        current_match = st.session_state.matches[st.session_state.current_match_idx]
        left_item = current_match[0]
        right_item = current_match[1]
        
        st.markdown(f"<div class='subtitle-text'>⚡ <b>{st.session_state.current_round}</b> ({st.session_state.current_match_idx + 1}/{len(st.session_state.matches)}) ⚡</div>", unsafe_allow_html=True)
        
        # 간격과 비율을 조절하여 버튼 위치 정렬 (가운데 정렬)
        col1, col_gap, col2 = st.columns([10, 2, 10])
        
        with col1:
            st.markdown(f"<div class='menu-card'><div class='emoji-icon'>{EMOJI_MAP.get(left_item)}</div></div>", unsafe_allow_html=True)
            if st.button(left_item, key=f"left_{st.session_state.current_round}_{st.session_state.current_match_idx}"):
                select_menu(left_item, right_item, left_item)
                st.rerun()
            
        with col2:
            st.markdown(f"<div class='menu-card'><div class='emoji-icon'>{EMOJI_MAP.get(right_item)}</div></div>", unsafe_allow_html=True)
            if st.button(right_item, key=f"right_{st.session_state.current_round}_{st.session_state.current_match_idx}"):
                select_menu(left_item, right_item, right_item)
                st.rerun()
