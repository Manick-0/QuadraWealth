"""
QuadraWealth — Main Landing Page
Streamlit multi-page app entry point.
"""
import streamlit as st
import os

st.set_page_config(
    page_title="QuadraWealth — Capital Manager",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS with Apple-style animations ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.main .block-container {
    padding-top: 1rem;
    max-width: 1200px;
}

/* ─── Apple-style Keyframe Animations ─── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes shimmer {
    0% { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes floatUp {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

/* ─── Hero ─── */
.hero-title {
    background: linear-gradient(135deg, #00D4AA 0%, #00B4D8 50%, #7B68EE 100%);
    background-size: 200% 200%;
    animation: gradientShift 6s ease infinite, fadeInUp 1s ease-out;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 4.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    color: rgba(250, 250, 250, 0.55);
    font-size: 1.35rem;
    text-align: center;
    margin-top: 0.5rem;
    font-weight: 300;
    letter-spacing: 0.02em;
    animation: fadeInUp 1s ease-out 0.2s both;
}

/* ─── Stat counters ─── */
.stat-row {
    display: flex;
    justify-content: center;
    gap: 3.5rem;
    margin: 2rem 0;
    animation: fadeInUp 1s ease-out 0.4s both;
}
.stat-item { text-align: center; }
.stat-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #00D4AA, #00B4D8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-label {
    font-size: 0.75rem;
    color: rgba(250,250,250,0.45);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 4px;
}

/* ─── Mode cards ─── */
.mode-card {
    background: linear-gradient(135deg, #1A1F2E 0%, #252B3B 100%);
    border: 1px solid rgba(0, 212, 170, 0.1);
    border-radius: 20px;
    padding: 2rem 1.5rem;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    cursor: pointer;
}
.mode-card:hover {
    border-color: rgba(0, 212, 170, 0.5);
    box-shadow: 0 16px 48px rgba(0, 212, 170, 0.12);
    transform: translateY(-8px);
}
.mode-icon { font-size: 2.5rem; margin-bottom: 0.8rem; }
.mode-title { font-size: 1.3rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.4rem; }
.mode-desc { color: rgba(250, 250, 250, 0.5); font-size: 0.85rem; line-height: 1.5; }

.card-anim-1 { animation: fadeInUp 0.8s ease-out 0.5s both; }
.card-anim-2 { animation: fadeInUp 0.8s ease-out 0.65s both; }
.card-anim-3 { animation: fadeInUp 0.8s ease-out 0.8s both; }
.card-anim-4 { animation: fadeInUp 0.8s ease-out 0.95s both; }

/* ─── How It Works section ─── */
.how-section {
    animation: fadeInUp 0.8s ease-out 1.1s both;
}
.algo-card {
    background: linear-gradient(135deg, #141824 0%, #1A1F2E 100%);
    border: 1px solid rgba(0, 212, 170, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 0.5rem 0;
    transition: all 0.3s ease;
}
.algo-card:hover {
    border-color: rgba(0, 212, 170, 0.25);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.algo-title {
    font-size: 1rem;
    font-weight: 700;
    color: #00D4AA;
    margin-bottom: 0.5rem;
}
.algo-text {
    color: rgba(250,250,250,0.6);
    font-size: 0.85rem;
    line-height: 1.6;
}
.algo-tag {
    display: inline-block;
    background: rgba(0, 212, 170, 0.1);
    color: #00D4AA;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-top: 8px;
    margin-right: 4px;
    letter-spacing: 0.05em;
}

/* ─── Divider ─── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 170, 0.3), transparent);
    margin: 2rem 0;
}

/* ─── Footer ─── */
.footer-section {
    text-align: center;
    padding: 2.5rem 0 1rem;
    animation: fadeIn 1s ease-out 1.4s both;
}
.footer-event {
    font-size: 0.85rem;
    font-weight: 600;
    color: rgba(250,250,250,0.4);
    text-transform: uppercase;
    letter-spacing: 0.15em;
}
.footer-name {
    font-size: 1rem;
    color: #00D4AA;
    font-weight: 700;
    margin-top: 6px;
}
.footer-sub {
    font-size: 0.75rem;
    color: rgba(250,250,250,0.25);
    margin-top: 4px;
}

/* ─── Sidebar ─── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117 0%, #141824 100%);
    border-right: 1px solid rgba(0, 212, 170, 0.1);
}
/* Rename 'app' to 'Home' in sidebar nav */
section[data-testid="stSidebar"] a[href="/"] span {
    visibility: hidden;
    position: relative;
}
section[data-testid="stSidebar"] a[href="/"] span::after {
    content: "Home";
    visibility: visible;
    position: absolute;
    left: 0;
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
        min_value=1000, max_value=10000000, value=50000, step=5000,
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

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.caption("QuadraWealth v1.0")

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
    <div class="mode-card card-anim-1">
        <div class="mode-icon">📈</div>
        <div class="mode-title">Stocks</div>
        <div class="mode-desc">AI-powered equity recommendations with real-time market data and RAG analysis.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="mode-card card-anim-2">
        <div class="mode-icon">🎯</div>
        <div class="mode-title">The Edge</div>
        <div class="mode-desc">Arbitrage detection & +EV bets across FanDuel, DraftKings, and Hard Rock.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="mode-card card-anim-3">
        <div class="mode-icon">🏦</div>
        <div class="mode-title">Savings & Yields</div>
        <div class="mode-desc">Dynamic yield finder powered by macroeconomic triggers and risk profiling.</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="mode-card card-anim-4">
        <div class="mode-icon">🏠</div>
        <div class="mode-title">Real Estate</div>
        <div class="mode-desc">Property screener with cap rate, cash-on-cash, and goal-based scoring.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── How It Works ──
st.markdown("""
<div class="how-section">
    <div style="text-align:center; margin-bottom:1.5rem;">
        <span style="font-size:1.6rem; font-weight:800; color:#FAFAFA;">How It Works</span>
        <div style="color:rgba(250,250,250,0.4); font-size:0.9rem; margin-top:4px;">The algorithms behind each mode — explained simply.</div>
    </div>
</div>
""", unsafe_allow_html=True)

h1, h2 = st.columns(2)

with h1:
    st.markdown("""
    <div class="algo-card">
        <div class="algo-title">📈 Stocks — RAG Scoring Engine</div>
        <div class="algo-text">
            We pull live data from <strong>yfinance</strong> for 20+ stocks, then use a
            <strong>vector database (ChromaDB)</strong> to find the most relevant financial news
            for each stock. The algorithm scores each stock out of 100 by combining:<br><br>
            • <strong>Momentum</strong> — Is the stock trending up or down over 30 days?<br>
            • <strong>Risk alignment</strong> — Does the stock's volatility (beta) match your tolerance?<br>
            • <strong>Value</strong> — Is the P/E ratio reasonable, or overvalued?<br>
            • <strong>News sentiment</strong> — Are recent headlines bullish or bearish?<br>
            • <strong>Dividends</strong> — Bonus points for conservative investors seeking income.<br><br>
            The final score determines the ranking — the higher the score, the stronger the buy signal.
        </div>
        <span class="algo-tag">ChromaDB</span>
        <span class="algo-tag">yfinance</span>
        <span class="algo-tag">Cosine Similarity</span>
        <span class="algo-tag">Multi-Factor Scoring</span>
    </div>
    """, unsafe_allow_html=True)

with h2:
    st.markdown("""
    <div class="algo-card">
        <div class="algo-title">🎯 The Edge — Arbitrage & Expected Value</div>
        <div class="algo-text">
            We pull <strong>live odds</strong> from The Odds API across FanDuel, DraftKings, and Hard Rock Bet.
            Two algorithms run simultaneously:<br><br>
            <strong>Arbitrage Scanner:</strong> When two sportsbooks disagree enough, the combined implied
            probability drops below 100%. You bet both sides and <strong>guarantee profit</strong> regardless
            of outcome.<br><br>
            <strong>+EV Finder:</strong> We calculate the <strong>consensus probability</strong> (average across
            all books) as the "true" chance. If one book's odds imply a lower probability, you have an edge.
            We use the <strong>Kelly Criterion</strong> (quarter-kelly for safety) to size each bet optimally.
        </div>
        <span class="algo-tag">Implied Probability</span>
        <span class="algo-tag">Kelly Criterion</span>
        <span class="algo-tag">Live Odds API</span>
    </div>
    """, unsafe_allow_html=True)

h3, h4 = st.columns(2)

with h3:
    st.markdown("""
    <div class="algo-card">
        <div class="algo-title">🏦 Savings & Yields — Macro-Trigger Allocation</div>
        <div class="algo-text">
            The algorithm monitors <strong>macroeconomic indicators</strong> — Fed rate, inflation (CPI),
            unemployment, GDP growth, and the yield curve spread — to determine the optimal
            allocation across savings vehicles:<br><br>
            • <strong>High-yield savings</strong> — Favored when rates are high and inflation is moderate<br>
            • <strong>T-Bills & bonds</strong> — Weighted heavily during yield curve inversions<br>
            • <strong>CDs</strong> — Locked in when rate cuts are expected<br>
            • <strong>I-Bonds</strong> — Boosted when inflation exceeds targets<br><br>
            Your <strong>risk profile</strong> shifts the base weights — conservative investors get
            more T-Bills, aggressive investors get more exposure to higher-yield instruments.
        </div>
        <span class="algo-tag">Macro Triggers</span>
        <span class="algo-tag">Risk-Weighted Allocation</span>
        <span class="algo-tag">Yield Optimization</span>
    </div>
    """, unsafe_allow_html=True)

with h4:
    st.markdown("""
    <div class="algo-card">
        <div class="algo-title">🏠 Real Estate — Goal-Based Property Scoring</div>
        <div class="algo-text">
            Every property is scored based on your <strong>investment goal</strong>:<br><br>
            <strong>Cash Flow:</strong> Prioritizes properties with the highest <strong>Net Operating Income (NOI)</strong>
            relative to price. NOI = (Monthly Rent × 12) − Operating Expenses (taxes, maintenance, vacancy).<br><br>
            <strong>Appreciation:</strong> Scores based on <strong>market growth rate</strong> and price-to-rent ratio.<br><br>
            <strong>Balanced:</strong> Combines both metrics with equal weight.<br><br>
            Each property also calculates <strong>Cap Rate</strong> (NOI ÷ Price) and <strong>Cash-on-Cash Return</strong>
            (annual cash flow ÷ down payment). Higher cap rates = better cash flow. Properties are ranked by
            composite score and displayed on an interactive map.
        </div>
        <span class="algo-tag">Cap Rate</span>
        <span class="algo-tag">NOI Analysis</span>
        <span class="algo-tag">Cash-on-Cash</span>
        <span class="algo-tag">Goal Scoring</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Navigation ──
st.info("Use the **sidebar** to navigate between modes, or click a page in the sidebar menu.", icon="🧭")

# ── Footer ──
st.markdown("""
<div class="footer-section">
    <div class="footer-event">Made for HackUSF 2026</div>
    <div class="footer-name">Manik Jindal (Nick)</div>
    <div class="footer-sub">FastAPI · Streamlit · ChromaDB · The Odds API · yfinance</div>
</div>
""", unsafe_allow_html=True)
