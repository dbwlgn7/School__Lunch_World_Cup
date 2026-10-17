import streamlit as st
import random
import uuid
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

# 페이지 및 테마 설정
st.set_page_config(page_title="급식 월드컵", page_icon="🍱", layout="centered")

# 챔피언스 2025 밴달 테마 CSS (레드/골드 엑센트, 다크 매트 배경, 기하학적 컷아웃, 네온 글로우)
st.markdown('''
<style>
/* 1. 전체 배경: 딥 매트 블랙 & 은은한 레드/골드 빛 
   단순한 검정색이 아닌, 발로란트 UI 특유의 고급스러운 그라데이션과 깊이감을 줍니다. */
.stApp {
    background: radial-gradient(circle at 15% 50%, rgba(204, 0, 0, 0.05), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(212, 175, 55, 0.05), transparent 25%),
                linear-gradient(135deg, #09090b 0%, #141417 100%);
    color: #e0e0e0;
}

/* 폰트 설정 (영문과 숫자에서 e스포츠 느낌을 주기 위해 임팩트 있는 산세리프 사용) */
h1, h2, h3, h4, h5, p, div, span, button {
    font-family: 'Pretendard', 'Malgun Gothic', sans-serif;
}

/* 2. 타이틀 (빛나는 황금색 & 붉은 네온 그림자) */
.title-text {
    text-align: center;
    font-size: 52px;
    font-weight: 900;
    margin-bottom: 5px;
    color: #f7e096;
    text-transform: uppercase;
    letter-spacing: 4px;
    text-shadow: 0 0 10px rgba(212, 175, 55, 0.7), 0 0 20px rgba(255, 0, 51, 0.4);
}

.subtitle-text {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 40px;
    color: #d4af37;
    letter-spacing: 2px;
}

/* 3. 메뉴 카드 (기하학적 라인 & 입체감)
   발로란트 특유의 '잘린 모서리(Clip-path)' 효과를 적용하여 미래지향적인 느낌을 줌 */
.menu-card {
    background: linear-gradient(145deg, #16161a 0%, #0d0d11 100%);
    border: 1px solid #2a2a35;
    padding: 30px 10px;
    text-align: center;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    /* 챔피언스 특유의 컷아웃 디자인 */
    clip-path: polygon(15px 0, 100% 0, 100% calc(100% - 15px), calc(100% - 15px) 100%, 0 100%, 0 15px);
    box-shadow: 10px 10px 30px rgba(0,0,0,0.9), inset 0 0 15px rgba(212, 175, 55, 0.05);
    border-bottom: 3px solid #cc0000;
    position: relative;
}

/* 카드 상단 골드 장식 */
.menu-card::before {
    content: '';
    position: absolute;
    top: 0; left: 15px; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #d4af37, transparent);
}

/* 이모티콘 텍스트 스타일 */
.emoji-icon {
    font-size: 90px;
    margin-bottom: 25px;
    filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.8));
    line-height: 1.2;
}

/* 4. 선택 버튼 (레드 & 골드 하이라이트) */
div.stButton > button {
    background: #0f0f13;
    color: #d4af37 !important;
    border: 1px solid #d4af37;
    border-radius: 0px !important;
    clip-path: polygon(10px 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%, 0 10px);
    padding: 15px;
    font-size: 22px;
    font-weight: 800;
    width: 100%;
    height: auto;
    min-height: 65px;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    white-space: normal;
    word-break: keep-all;
    text-transform: uppercase;
}

/* 호버 시 강렬한 크림슨 레드 & 글로우 이펙트 */
div.stButton > button:hover {
    background: linear-gradient(90deg, #cc0000 0%, #ff0033 100%);
    color: #ffffff !important;
    border: 1px solid #ff3366;
    box-shadow: 0 0 20px rgba(255, 0, 51, 0.6), inset 0 0 10px rgba(255,255,255,0.3);
    transform: scale(1.02);
}

div.stButton > button:active {
    transform: scale(0.98);
}

/* 5. 대시보드 박스 (Features Overview 스타일) */
.glow-box {
    background: linear-gradient(180deg, rgba(20, 20, 25, 0.9) 0%, rgba(10, 10, 12, 0.9) 100%);
    border: 1px solid #333;
    border-top: 2px solid #cc0000;
    padding: 25px;
    border-radius: 4px;
    margin-bottom: 30px;
    box-shadow: 0 10px 20px rgba(0,0,0,0.6);
}

/* 승률 차트 스타일링 덮어쓰기 위해 컨테이너 여백 확보 */
.stPlotlyChart {
    background: transparent !important;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 10px;
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
    st.markdown("<h2 class='title-text' style='font-size: 32px; margin-top: 60px;'>PERFORMANCE ANALYTICS</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 REFRESH DATA", key="refresh_stats"):
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
            <h4 style="color: #d4af37; margin-bottom: 10px;">LIVE MATCH TRACKING</h4>
            <p style="color: #fff; font-size: 18px;">총 <b>{total_records}</b>건의 대결 기록 (<b>{total_games}</b> 게임)</p>
            <p style="font-size: 13px; color: #777;">* 게임을 끝까지 마치지 않고 진행 중에 남긴 대결 결과도 모두 집계에 포함됩니다.</p>
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
            # 테마 색상 적용 (크림슨 레드)
            fig = px.bar(
                plot_df, x='승률(%)_raw', y='반찬 이름', orientation='h',
                labels={'승률(%)_raw': 'WIN RATE (%)', '반찬 이름': ''},
                color_discrete_sequence=['#cc0000']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e0e0e0', family='Pretendard, sans-serif'),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            # 막대그래프 두께 조절 및 호버 효과
            fig.update_traces(marker_line_color='#ff3366', marker_line_width=1.5, opacity=0.9)
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
st.markdown("<div class='title-text'>CHAMPIONS 급식 월드컵</div>", unsafe_allow_html=True)

if st.session_state.is_done:
    st.markdown(f"<div class='subtitle-text'>FINAL WINNER: <span style='color:#ff0033;'>{st.session_state.winner}</span></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'''
        <div class='menu-card'>
            <div class='emoji-icon' style='font-size:120px;'>{EMOJI_MAP.get(st.session_state.winner)}</div>
        </div>
        <br>
        ''', unsafe_allow_html=True)
        if st.button("START NEW JOURNEY", key="restart_btn_end"):
            reset_game()
            st.rerun()
            
    show_analytics()
    
else:
    if st.session_state.locked:
        st.error("데이터베이스 저장 확인이 필요하여 진행이 잠겼습니다. 오류를 확인해 주세요.")
    else:
        current_match = st.session_state.matches[st.session_state.current_match_idx]
        left_item = current_match[0]
        right_item = current_match[1]
        
        # 8강 -> ROUND 1 (8강) 등으로 e스포츠 느낌 강조
        round_display = f"ROUND: {st.session_state.current_round} ({st.session_state.current_match_idx + 1}/{len(st.session_state.matches)})"
        st.markdown(f"<div class='subtitle-text'>{round_display}</div>", unsafe_allow_html=True)
        
        # 간격과 비율을 조절하여 버튼 위치 정렬 (가운데 정렬)
        col1, col_gap, col2 = st.columns([10, 1, 10])
        
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
