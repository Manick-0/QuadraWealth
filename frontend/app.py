"""
QuadraWealth — Main Landing Page
Streamlit multi-page app entry point.
"""
import streamlit as st

st.set_page_config(
    page_title="QuadraWealth — Capital Manager",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero-title {
    background: linear-gradient(135deg, #00D4AA 0%, #00B4D8 50%, #7B68EE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 4rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0;
    line-height: 1.1;
}

.hero-subtitle {
    color: rgba(250, 250, 250, 0.6);
    font-size: 1.3rem;
    text-align: center;
    margin-top: 0.5rem;
    font-weight: 300;
}

.mode-card {
    background: linear-gradient(135deg, #1A1F2E 0%, #252B3B 100%);
    border: 1px solid rgba(0, 212, 170, 0.12);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.mode-card:hover {
    border-color: rgba(0, 212, 170, 0.4);
    box-shadow: 0 12px 40px rgba(0, 212, 170, 0.1);
    transform: translateY(-4px);
}
.mode-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}
.mode-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 0.5rem;
}
.mode-desc {
    color: rgba(250, 250, 250, 0.5);
    font-size: 0.9rem;
    line-height: 1.5;
}

.stat-row {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-top: 2rem;
    margin-bottom: 2rem;
}
.stat-item {
    text-align: center;
}
.stat-value {
    font-size: 2rem;
    font-weight: 800;
    color: #00D4AA;
}
.stat-label {
    font-size: 0.8rem;
    color: rgba(250,250,250,0.5);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 170, 0.3), transparent);
    margin: 2rem 0;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117 0%, #141824 100%);
    border-right: 1px solid rgba(0, 212, 170, 0.1);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### 💎 QuadraWealth")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("#### User Profile")
    risk = st.select_slider(
        "Risk Tolerance",
        options=["conservative", "moderate", "aggressive"],
        value="moderate",
        key="risk_tolerance",
    )

    sectors = st.multiselect(
        "Preferred Sectors",
        ["tech", "finance", "healthcare", "consumer", "energy"],
        default=["tech", "finance"],
        key="preferred_sectors",
    )

    capital = st.number_input(
        "Investment Capital ($)",
        min_value=1000,
        max_value=10000000,
        value=50000,
        step=5000,
        key="capital",
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("#### System Status")
    import os
    import requests as _req
    _backend = "http://localhost:8000"
    try:
        _backend = st.secrets["BACKEND_URL"]
    except Exception:
        _backend = os.environ.get("BACKEND_URL", "http://localhost:8000")
    try:
        r = _req.get(f"{_backend}/health", timeout=5)
        if r.status_code == 200:
            st.success("Backend Online", icon="✅")
        else:
            st.error("Backend Error", icon="❌")
    except Exception:
        st.warning("Backend Offline", icon="⚠️")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.caption("Built for HackUSF 2026")

# ── Hero Section ──
st.markdown("")
st.markdown('<div class="hero-title">QuadraWealth</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Four modes. One platform. Total capital control.</div>',
    unsafe_allow_html=True,
)

st.markdown("")

# ── Stats Row ──
st.markdown("""
<div class="stat-row">
    <div class="stat-item">
        <div class="stat-value">4</div>
        <div class="stat-label">Investment Modes</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">50+</div>
        <div class="stat-label">Properties Tracked</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">3</div>
        <div class="stat-label">Sportsbooks</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">RAG</div>
        <div class="stat-label">AI-Powered</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Mode Cards ──
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-icon">📈</div>
        <div class="mode-title">Stocks</div>
        <div class="mode-desc">AI-powered equity recommendations with real-time market data and RAG analysis.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-icon">🎯</div>
        <div class="mode-title">The Edge</div>
        <div class="mode-desc">Arbitrage detection & +EV bets across FanDuel, DraftKings, and Hard Rock.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-icon">🏦</div>
        <div class="mode-title">Savings & Yields</div>
        <div class="mode-desc">Dynamic yield finder powered by macroeconomic triggers and risk profiling.</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="mode-card">
        <div class="mode-icon">🏠</div>
        <div class="mode-title">Real Estate</div>
        <div class="mode-desc">Property screener with cap rate, cash-on-cash, and goal-based scoring.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown("")

# ── Navigation hint ──
st.info("Use the **sidebar** to navigate between modes, or click a page in the sidebar menu.", icon="🧭")

st.markdown("")
st.markdown("""
<div style="text-align: center; padding: 2rem 0 1rem; color: rgba(250,250,250,0.4); font-size: 0.9rem;">
    Made by <span style="color: #00D4AA; font-weight: 600;">Manik Jindal (Nick)</span>
</div>
""", unsafe_allow_html=True)
