import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(
    page_title="🎵 Music Trends Dashboard",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif !important;
        color: #f8f8f2 !important;
    }
    
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(120deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: gradient 3s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .subtitle {
        font-family: 'Space Mono', monospace;
        color: #a0a0a0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(255, 107, 107, 0.2);
    }
    
    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #ff6b6b;
    }
    
    .metric-label {
        font-family: 'Space Mono', monospace;
        color: #888;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    .section-header {
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #f8f8f2;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255, 107, 107, 0.3);
    }
    
    .insight-box {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(254, 202, 87, 0.1));
        border-left: 4px solid #ff6b6b;
        padding: 1rem 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
        font-family: 'Space Mono', monospace;
        color: #d0d0d0;
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
    }
    
    .stSlider > div > div {
        background: rgba(255, 107, 107, 0.3);
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f23 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    div[data-testid="stSidebar"] .stMarkdown {
        color: #f8f8f2;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """데이터 로드 및 전처리"""
    import os
    
    # 스크립트 파일 위치 기준 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    df1 = pd.read_csv(os.path.join(script_dir, 'track_data_final.csv'))
    df2 = pd.read_csv(os.path.join(script_dir, 'spotify_data_clean.csv'))
    
    # 곡 길이 통일 (분 단위)
    df1['duration_min'] = df1['track_duration_ms'] / 60000
    df2['duration_min'] = df2['track_duration_min']
    
    # 공통 컬럼만 선택
    common_cols = ['track_id', 'track_name', 'track_popularity', 'explicit', 
                   'artist_name', 'artist_popularity', 'artist_followers',
                   'album_release_date', 'album_type', 'duration_min']
    
    df1_clean = df1[common_cols].copy()
    df2_clean = df2[['track_id', 'track_name', 'track_popularity', 'explicit',
                     'artist_name', 'artist_popularity', 'artist_followers',
                     'album_release_date', 'album_type', 'duration_min']].copy()
    
    # 합치기
    df = pd.concat([df1_clean, df2_clean], ignore_index=True)
    
    # 중복 제거
    df = df.drop_duplicates(subset=['track_id'])
    
    # 연도 추출
    df['year'] = pd.to_datetime(df['album_release_date'], errors='coerce').dt.year
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)
    
    # 2000년 이후 데이터만 사용 (샘플 수 충분)
    df = df[df['year'] >= 2000]
    
    return df


def create_trend_chart(df_yearly, y_col, title, color, y_title):
    """트렌드 차트 생성"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_yearly['year'],
        y=df_yearly[y_col],
        mode='lines+markers',
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color, line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(color)) + [0.1])}',
        hovertemplate='<b>%{x}년</b><br>' + y_title + ': %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color='#f8f8f2', family='Outfit')),
        xaxis=dict(
            title='연도',
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#a0a0a0', family='Space Mono'),
            titlefont=dict(color='#a0a0a0', family='Space Mono')
        ),
        yaxis=dict(
            title=y_title,
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#a0a0a0', family='Space Mono'),
            titlefont=dict(color='#a0a0a0', family='Space Mono')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=60, r=30, t=60, b=60),
        hovermode='x unified'
    )
    
    return fig


def create_album_type_chart(df, year_range):
    """앨범 타입 비율 차트"""
    df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    
    type_by_year = df_filtered.groupby(['year', 'album_type']).size().unstack(fill_value=0)
    type_pct = type_by_year.div(type_by_year.sum(axis=1), axis=0) * 100
    
    fig = go.Figure()
    
    colors = {'album': '#ff6b6b', 'single': '#48dbfb', 'compilation': '#feca57'}
    labels = {'album': '앨범', 'single': '싱글', 'compilation': '컴필레이션'}
    
    for col in type_pct.columns:
        fig.add_trace(go.Scatter(
            x=type_pct.index,
            y=type_pct[col],
            name=labels.get(col, col),
            mode='lines',
            stackgroup='one',
            line=dict(width=0.5, color=colors.get(col, '#888')),
            fillcolor=colors.get(col, '#888'),
            hovertemplate='<b>%{x}년</b><br>' + labels.get(col, col) + ': %{y:.1f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(text='📀 앨범 타입 비율 변화', font=dict(size=20, color='#f8f8f2', family='Outfit')),
        xaxis=dict(
            title='연도',
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#a0a0a0', family='Space Mono'),
            titlefont=dict(color='#a0a0a0', family='Space Mono')
        ),
        yaxis=dict(
            title='비율 (%)',
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#a0a0a0', family='Space Mono'),
            titlefont=dict(color='#a0a0a0', family='Space Mono'),
            range=[0, 100]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=60, r=30, t=60, b=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='#a0a0a0', family='Space Mono')
        ),
        hovermode='x unified'
    )
    
    return fig


def create_combined_chart(df_yearly):
    """곡 길이 + 인기도 복합 차트"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 곡 길이
    fig.add_trace(
        go.Scatter(
            x=df_yearly['year'],
            y=df_yearly['duration_min'],
            name='평균 곡 길이',
            mode='lines+markers',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}년</b><br>곡 길이: %{y:.2f}분<extra></extra>'
        ),
        secondary_y=False
    )
    
    # 인기도
    fig.add_trace(
        go.Scatter(
            x=df_yearly['year'],
            y=df_yearly['track_popularity'],
            name='평균 인기도',
            mode='lines+markers',
            line=dict(color='#48dbfb', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}년</b><br>인기도: %{y:.1f}<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_layout(
        title=dict(text='🎵 곡 길이 vs 인기도 트렌드', font=dict(size=20, color='#f8f8f2', family='Outfit')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(l=60, r=60, t=60, b=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5,
            font=dict(color='#a0a0a0', family='Space Mono')
        ),
        hovermode='x unified'
    )
    
    fig.update_xaxes(
        title_text='연도',
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='#a0a0a0', family='Space Mono'),
        titlefont=dict(color='#a0a0a0', family='Space Mono')
    )
    
    fig.update_yaxes(
        title_text='곡 길이 (분)',
        gridcolor='rgba(255,255,255,0.1)',
        tickfont=dict(color='#ff6b6b', family='Space Mono'),
        titlefont=dict(color='#ff6b6b', family='Space Mono'),
        secondary_y=False
    )
    
    fig.update_yaxes(
        title_text='인기도',
        tickfont=dict(color='#48dbfb', family='Space Mono'),
        titlefont=dict(color='#48dbfb', family='Space Mono'),
        secondary_y=True
    )
    
    return fig


# 메인 앱
def main():
    # 타이틀
    st.markdown('<h1 class="main-title">🎵 Music Trends Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">2000 ~ 2025 스포티파이 음악 트렌드 분석</p>', unsafe_allow_html=True)
    
    # 데이터 로드
    df = load_data()
    
    # 사이드바
    with st.sidebar:
        st.markdown("### 🎛️ 필터 설정")
        
        year_range = st.slider(
            "연도 범위",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=(2010, 2025),
            step=1
        )
        
        st.markdown("---")
        
        album_types = st.multiselect(
            "앨범 타입",
            options=['album', 'single', 'compilation'],
            default=['album', 'single', 'compilation'],
            format_func=lambda x: {'album': '앨범', 'single': '싱글', 'compilation': '컴필레이션'}[x]
        )
        
        st.markdown("---")
        st.markdown("### 📊 데이터 정보")
        st.markdown(f"**총 트랙 수:** {len(df):,}곡")
        st.markdown(f"**아티스트 수:** {df['artist_name'].nunique():,}명")
        st.markdown(f"**연도 범위:** {int(df['year'].min())} ~ {int(df['year'].max())}")
    
    # 필터링
    df_filtered = df[
        (df['year'] >= year_range[0]) & 
        (df['year'] <= year_range[1]) &
        (df['album_type'].isin(album_types))
    ]
    
    # 연도별 집계
    df_yearly = df_filtered.groupby('year').agg({
        'duration_min': 'mean',
        'track_popularity': 'mean',
        'explicit': 'mean',
        'track_id': 'count'
    }).reset_index()
    df_yearly['explicit_pct'] = df_yearly['explicit'] * 100
    df_yearly.rename(columns={'track_id': 'track_count'}, inplace=True)
    
    # 주요 지표 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df_filtered):,}</div>
            <div class="metric-label">총 트랙 수</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_duration = df_filtered['duration_min'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #48dbfb;">{avg_duration:.1f}분</div>
            <div class="metric-label">평균 곡 길이</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_popularity = df_filtered['track_popularity'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #feca57;">{avg_popularity:.0f}</div>
            <div class="metric-label">평균 인기도</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        explicit_pct = df_filtered['explicit'].mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #ff9ff3;">{explicit_pct:.1f}%</div>
            <div class="metric-label">Explicit 비율</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 복합 차트 (곡 길이 + 인기도)
    st.plotly_chart(create_combined_chart(df_yearly), use_container_width=True)
    
    # 인사이트
    recent_duration = df_yearly[df_yearly['year'] >= 2020]['duration_min'].mean()
    old_duration = df_yearly[df_yearly['year'] < 2015]['duration_min'].mean()
    duration_change = ((recent_duration - old_duration) / old_duration) * 100
    
    trend_direction = "짧아지는" if duration_change < 0 else "길어지는"
    st.markdown(f"""
    <div class="insight-box">
        💡 <b>인사이트:</b> 2015년 이전 대비 2020년 이후 곡 길이가 평균 <b>{abs(duration_change):.1f}%</b> {trend_direction} 추세입니다.
        스트리밍 시대에 맞춰 곡이 점점 짧아지고 있어요!
    </div>
    """, unsafe_allow_html=True)
    
    # 2열 차트
    col1, col2 = st.columns(2)
    
    with col1:
        fig_explicit = create_trend_chart(
            df_yearly, 'explicit_pct', 
            '🔞 Explicit 비율 변화', '#ff9ff3', 'Explicit 비율 (%)'
        )
        st.plotly_chart(fig_explicit, use_container_width=True)
    
    with col2:
        fig_album = create_album_type_chart(df, year_range)
        st.plotly_chart(fig_album, use_container_width=True)
    
    # 연도별 트랙 수
    fig_count = go.Figure()
    fig_count.add_trace(go.Bar(
        x=df_yearly['year'],
        y=df_yearly['track_count'],
        marker_color='rgba(255, 107, 107, 0.7)',
        marker_line=dict(color='#ff6b6b', width=1),
        hovertemplate='<b>%{x}년</b><br>트랙 수: %{y:,}<extra></extra>'
    ))
    
    fig_count.update_layout(
        title=dict(text='📈 연도별 트랙 수', font=dict(size=20, color='#f8f8f2', family='Outfit')),
        xaxis=dict(
            title='연도',
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#a0a0a0', family='Space Mono'),
            titlefont=dict(color='#a0a0a0', family='Space Mono')
        ),
        yaxis=dict(
            title='트랙 수',
            gridcolor='rgba(255,255,255,0.1)',
            tickfont=dict(color='#a0a0a0', family='Space Mono'),
            titlefont=dict(color='#a0a0a0', family='Space Mono')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=60, r=30, t=60, b=60)
    )
    
    st.plotly_chart(fig_count, use_container_width=True)
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <p style="text-align: center; color: #666; font-family: 'Space Mono', monospace; font-size: 0.85rem;">
        데이터 출처: Spotify | 총 17,000+ 트랙 분석
    </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
