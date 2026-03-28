"""
QuadraWealth — Main Landing Page
Streamlit multi-page app entry point.
"""
import os
import streamlit as st

st.set_page_config(
    page_title="QuadraWealth — Capital Manager",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with Apple-style animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* ── Apple-style slide-in animations ── */
@keyframes slideUp {
    from { opacity: 0; transform: translateY(60px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-80px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(80px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.85); }
    to { opacity: 1; transform: scale(1); }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 170, 0.1); }
    50% { box-shadow: 0 0 40px rgba(0, 212, 170, 0.25); }
}

/* Hero */
.hero-title {
    background: linear-gradient(135deg, #00D4AA 0%, #00B4D8 50%, #7B68EE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 4.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0;
    line-height: 1.1;
    animation: scaleIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.hero-subtitle {
    color: rgba(250, 250, 250, 0.6);
    font-size: 1.35rem;
    text-align: center;
    margin-top: 0.8rem;
    font-weight: 300;
    animation: slideUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.15s both;
}

/* Stats row */
.stat-row {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin: 2.5rem 0;
    animation: slideUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
}
.stat-item { text-align: center; }
.stat-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #00D4AA;
}
.stat-label {
    font-size: 0.75rem;
    color: rgba(250,250,250,0.5);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 4px;
}

/* Mode cards — staggered slide-in */
.mode-card {
    background: linear-gradient(135deg, #1A1F2E 0%, #252B3B 100%);
    border: 1px solid rgba(0, 212, 170, 0.12);
    border-radius: 20px;
    padding: 2rem 1.5rem;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    animation: pulseGlow 4s ease-in-out infinite;
}
.card-1 { animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.4s both; }
.card-2 { animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.55s both; }
.card-3 { animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.7s both; }
.card-4 { animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.85s both; }

.mode-card:hover {
    border-color: rgba(0, 212, 170, 0.5);
    box-shadow: 0 20px 60px rgba(0, 212, 170, 0.15);
    transform: translateY(-8px) scale(1.02);
}
.mode-icon { font-size: 3rem; margin-bottom: 1rem; }
.mode-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #FAFAFA;
    margin-bottom: 0.5rem;
}
.mode-desc {
    color: rgba(250, 250, 250, 0.5);
    font-size: 0.88rem;
    line-height: 1.5;
}

/* Algorithm explanation section */
.algo-section {
    animation: slideUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) 1.0s both;
}
.algo-card {
    background: linear-gradient(135deg, #141824 0%, #1A1F2E 100%);
    border: 1px solid rgba(0, 212, 170, 0.08);
    border-radius: 16px;
    padding: 1.8rem;
    margin: 1rem 0;
    transition: all 0.3s ease;
}
.algo-card:hover {
    border-color: rgba(0, 212, 170, 0.25);
    transform: translateX(6px);
}
.algo-number {
    display: inline-block;
    background: linear-gradient(135deg, #00D4AA, #00B4D8);
    color: #0E1117;
    font-weight: 800;
    font-size: 0.85rem;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    margin-right: 10px;
}
.algo-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #FAFAFA;
    display: inline;
}
.algo-desc {
    color: rgba(250,250,250,0.55);
    font-size: 0.9rem;
    margin-top: 8px;
    line-height: 1.6;
    padding-left: 38px;
}

/* Dividers */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 170, 0.3), transparent);
    margin: 2rem 0;
}

/* Footer / credit */
.footer-section {
    text-align: center;
    padding: 3rem 0 1.5rem;
    animation: fadeIn 1s ease 1.5s both;
}
.footer-hackusf {
    color: rgba(250,250,250,0.3);
    font-size: 0.85rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
}
.footer-author {
    color: #00D4AA;
    font-size: 1rem;
    font-weight: 600;
    margin-top: 6px;
}
.footer-tagline {
    color: rgba(250,250,250,0.2);
    font-size: 0.75rem;
    margin-top: 8px;
    font-style: italic;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117 0%, #141824 100%);
    border-right: 1px solid rgba(0, 212, 170, 0.1);
}

/* Hide ALL Streamlit branding and chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {display: none !important;}
div[data-testid="stToolbar"] {display: none !important;}
div[data-testid="stDecoration"] {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}
.stDeployButton {display: none !important;}
#stDecoration {display: none !important;}
.viewerBadge_container__r5tak {display: none !important;}
.styles_viewerBadge__CvC9N {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### QuadraWealth")
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
    <div class="mode-card card-1">
        <div class="mode-icon">📈</div>
        <div class="mode-title">Stocks</div>
        <div class="mode-desc">AI-powered equity recommendations with real-time market data and RAG analysis.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="mode-card card-2">
        <div class="mode-icon">🎯</div>
        <div class="mode-title">The Edge</div>
        <div class="mode-desc">Arbitrage detection & +EV bets across FanDuel, DraftKings, and Hard Rock.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="mode-card card-3">
        <div class="mode-icon">🏦</div>
        <div class="mode-title">Savings & Yields</div>
        <div class="mode-desc">Dynamic yield finder powered by macroeconomic triggers and risk profiling.</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="mode-card card-4">
        <div class="mode-icon">🏠</div>
        <div class="mode-title">Real Estate</div>
        <div class="mode-desc">Property screener with cap rate, cash-on-cash, and goal-based scoring.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── How It Works — Algorithm Explanations ──
st.markdown('<div class="algo-section">', unsafe_allow_html=True)
st.markdown("### How It Works")
st.caption("Each module uses a specialized algorithm to surface the best opportunities. Here's what's happening under the hood.")

st.markdown("""
<div class="algo-card">
    <span class="algo-number">1</span>
    <span class="algo-title">Stocks — Multi-Signal Scoring Engine</span>
    <div class="algo-desc">
        We pull live price data for 25+ stocks, then score each on a 0–100 scale using <strong>six signals</strong>:
        sector match, 1-month momentum, risk-profile alignment (beta), valuation (P/E ratio), dividend yield,
        and RAG-powered news sentiment. ChromaDB embeds 50+ financial news articles and finds semantically
        similar stories to gauge sector outlook. The highest-scoring stocks surface as your top picks.
    </div>
</div>

<div class="algo-card">
    <span class="algo-number">2</span>
    <span class="algo-title">The Edge — Expected Value Calculator</span>
    <div class="algo-desc">
        Real-time odds from FanDuel, DraftKings, and Hard Rock Bet are compared line-by-line.
        For each outcome, we calculate the <strong>consensus "true" probability</strong> by averaging implied
        probabilities across all books, then compare it to each individual book's odds. When a book's price
        implies a lower probability than our consensus, that's a <strong>+EV bet</strong> — a mathematical
        edge. We also scan for <strong>arbitrage</strong>, where the combined implied probability across
        books drops below 100%, guaranteeing profit regardless of outcome.
    </div>
</div>

<div class="algo-card">
    <span class="algo-number">3</span>
    <span class="algo-title">Savings & Yields — Macro-Trigger Allocation</span>
    <div class="algo-desc">
        We analyze <strong>macroeconomic conditions</strong> — interest rates, inflation, GDP growth, and
        unemployment — to dynamically shift your allocation between high-yield savings, CDs, bonds,
        and money-market funds. When rates rise, we lean into short-term CDs. When inflation spikes,
        we favor I-bonds and TIPS. Your risk tolerance adjusts the aggressiveness of the rebalancing.
    </div>
</div>

<div class="algo-card">
    <span class="algo-number">4</span>
    <span class="algo-title">Real Estate — Goal-Based Property Scoring</span>
    <div class="algo-desc">
        Each property is scored on <strong>cap rate</strong> (net operating income / property price),
        <strong>cash-on-cash return</strong> (annual pre-tax cash flow / total cash invested), and how well it
        matches your investment goals (appreciation vs. cash flow vs. house-hack). Properties near strong
        job markets and with low price-to-rent ratios rank highest. We screen 50+ listings and surface the
        top-scoring opportunities for your profile.
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("")

# ── Footer / Credits ──
st.markdown("""
<div class="footer-section">
    <div class="footer-hackusf">Made for HackUSF 2026</div>
    <div class="footer-author">Made by Manik Jindal (Nick)</div>
    <div class="footer-tagline">Four modes. Real data. Real edge.</div>
</div>
""", unsafe_allow_html=True)
