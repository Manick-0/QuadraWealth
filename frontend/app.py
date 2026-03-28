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

# ── Premium CSS with Apple-style animations ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

/* ── Hide ALL Streamlit chrome ── */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header[data-testid="stHeader"] {display: none !important;}
div[data-testid="stToolbar"] {display: none !important;}
div[data-testid="stDecoration"] {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}
.stDeployButton {display: none !important;}
#stDecoration {display: none !important;}
.viewerBadge_container__r5tak {display: none !important;}
.styles_viewerBadge__CvC9N {display: none !important;}

/* Hide keyboard_double arrow icon */
button[kind="header"] {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}
.css-1rs6os {display: none !important;}
.css-10trblm {display: none !important;}

/* Fix sidebar "app" label */
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:first-child span {
    font-size: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:first-child span::after {
    content: "Home";
    font-size: 14px !important;
}

.main .block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

/* ── Apple-style Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-40px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInRight {
    from { opacity: 0; transform: translateX(40px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
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

/* Hero */
.hero-title {
    background: linear-gradient(135deg, #00D4AA 0%, #00B4D8 30%, #7B68EE 60%, #00D4AA 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 4.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0;
    line-height: 1.1;
    animation: fadeInUp 1s ease-out, gradientShift 6s ease infinite;
}
.hero-subtitle {
    color: rgba(250, 250, 250, 0.6);
    font-size: 1.3rem;
    text-align: center;
    margin-top: 0.5rem;
    font-weight: 300;
    animation: fadeInUp 1s ease-out 0.2s both;
}

/* Stats */
.stat-row {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin: 2.5rem 0;
    animation: fadeInUp 1s ease-out 0.4s both;
}
.stat-item { text-align: center; }
.stat-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #00D4AA;
}
.stat-label {
    font-size: 0.75rem;
    color: rgba(250,250,250,0.4);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 4px;
}

/* Mode Cards */
.mode-card {
    background: linear-gradient(135deg, #1A1F2E 0%, #252B3B 100%);
    border: 1px solid rgba(0, 212, 170, 0.12);
    border-radius: 20px;
    padding: 2rem 1.5rem;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    min-height: 260px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    animation: scaleIn 0.6s ease-out both;
}
.mode-card:nth-child(1) { animation-delay: 0.5s; }
.mode-card:nth-child(2) { animation-delay: 0.65s; }
.mode-card:nth-child(3) { animation-delay: 0.8s; }
.mode-card:nth-child(4) { animation-delay: 0.95s; }

.mode-card:hover {
    border-color: rgba(0, 212, 170, 0.5);
    box-shadow: 0 16px 48px rgba(0, 212, 170, 0.12);
    transform: translateY(-6px);
}
.mode-icon { font-size: 2.8rem; margin-bottom: 1rem; }
.mode-title { font-size: 1.3rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.5rem; }
.mode-desc { color: rgba(250, 250, 250, 0.45); font-size: 0.85rem; line-height: 1.6; }

/* Algorithm Section */
.algo-section {
    animation: fadeInUp 0.8s ease-out both;
    margin: 1rem 0;
}
.algo-card {
    background: linear-gradient(135deg, #141824 0%, #1A1F2E 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.8rem;
    margin: 0.8rem 0;
    transition: all 0.3s ease;
}
.algo-card:hover {
    border-color: rgba(0, 212, 170, 0.2);
    transform: translateX(4px);
}
.algo-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #00D4AA;
    margin-bottom: 0.5rem;
}
.algo-body {
    color: rgba(250,250,250,0.6);
    font-size: 0.9rem;
    line-height: 1.7;
}
.algo-tag {
    display: inline-block;
    background: rgba(0, 212, 170, 0.1);
    color: #00D4AA;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-right: 6px;
    margin-top: 8px;
    letter-spacing: 0.05em;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 170, 0.3), transparent);
    margin: 2rem 0;
}

/* Footer */
.footer-credits {
    text-align: center;
    padding: 2.5rem 0 1rem;
    animation: fadeInUp 1s ease-out 1.5s both;
}
.footer-hackusf {
    color: rgba(250,250,250,0.3);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-weight: 500;
}
.footer-author {
    color: #00D4AA;
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 6px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0E1117 0%, #141824 100%);
    border-right: 1px solid rgba(0, 212, 170, 0.1);
}
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
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── How It Works — Algorithm Explanations ──
st.markdown("""
<div style="text-align:center; animation: fadeInUp 0.8s ease-out 1s both;">
    <div style="font-size:1.8rem; font-weight:800; color:#FAFAFA; margin-bottom:0.3rem;">How It Works</div>
    <div style="color:rgba(250,250,250,0.4); font-size:0.95rem;">The algorithms behind each mode, explained simply.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

left, right = st.columns(2)

with left:
    st.markdown("""
    <div class="algo-section" style="animation-delay: 1.1s;">
        <div class="algo-card">
            <div class="algo-title">📈 Stocks — RAG-Powered Scoring</div>
            <div class="algo-body">
                We pull real-time prices from Yahoo Finance, then query our <strong>vector database</strong> (ChromaDB)
                for the latest financial news related to each stock's sector. A scoring algorithm combines:<br><br>
                <strong>1.</strong> One-month price momentum (trending up or down?)<br>
                <strong>2.</strong> Risk alignment (does the stock's volatility match your tolerance?)<br>
                <strong>3.</strong> Value metrics (is the P/E ratio attractive?)<br>
                <strong>4.</strong> News sentiment (are headlines bullish or bearish?)<br>
                <strong>5.</strong> Dividend yield bonus for conservative investors<br><br>
                Each stock gets a <strong>score out of 100</strong>. The higher the score, the stronger the recommendation for your profile.
            </div>
            <div>
                <span class="algo-tag">ChromaDB</span>
                <span class="algo-tag">yfinance</span>
                <span class="algo-tag">Momentum</span>
                <span class="algo-tag">Sentiment</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="algo-section" style="animation-delay: 1.3s;">
        <div class="algo-card">
            <div class="algo-title">🏦 Savings — Macro-Trigger Allocation</div>
            <div class="algo-body">
                Instead of fixed splits, our yield allocator <strong>reacts to live economic conditions</strong>.
                It monitors the Fed Funds Rate, inflation (CPI), and the yield curve to dynamically shift your money:<br><br>
                <strong>Rising rates?</strong> → More in high-yield savings and short-term bonds<br>
                <strong>Inverted yield curve?</strong> → Defensive allocation, reduce risk exposure<br>
                <strong>Low inflation?</strong> → Shift toward growth assets and longer-term instruments<br><br>
                Your risk tolerance adjusts the sensitivity — aggressive profiles take bigger swings, conservative ones stay steady.
            </div>
            <div>
                <span class="algo-tag">Fed Rate</span>
                <span class="algo-tag">CPI</span>
                <span class="algo-tag">Yield Curve</span>
                <span class="algo-tag">Dynamic</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown("""
    <div class="algo-section" style="animation-delay: 1.2s;">
        <div class="algo-card">
            <div class="algo-title">🎯 The Edge — Arbitrage & Expected Value</div>
            <div class="algo-body">
                We pull <strong>live odds from The Odds API</strong> across FanDuel, DraftKings, and Hard Rock Bet,
                then run two scans:<br><br>
                <strong>Arbitrage:</strong> If the combined implied probability across two books is under 100%,
                you can bet both sides and <em>guarantee profit</em> regardless of who wins.<br><br>
                <strong>+EV (Expected Value):</strong> We calculate the <em>consensus probability</em> by averaging
                implied odds across all books. If one book's line is significantly off consensus, that's a +EV bet.
                We size the recommended stake using the <strong>Kelly Criterion</strong> (quarter-Kelly for safety).
            </div>
            <div>
                <span class="algo-tag">Odds API</span>
                <span class="algo-tag">Arbitrage</span>
                <span class="algo-tag">Kelly Criterion</span>
                <span class="algo-tag">Live</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="algo-section" style="animation-delay: 1.4s;">
        <div class="algo-card">
            <div class="algo-title">🏠 Real Estate — Goal-Based Screening</div>
            <div class="algo-body">
                Every property gets scored based on <strong>your investment goal</strong>:<br><br>
                <strong>Cash flow?</strong> → Prioritizes high cap rate and low price-to-rent ratio<br>
                <strong>Appreciation?</strong> → Weights properties in high-growth zip codes<br>
                <strong>Balanced?</strong> → Blends both metrics equally<br><br>
                We calculate <strong>NOI</strong> (Net Operating Income), <strong>Cap Rate</strong>,
                and <strong>Cash-on-Cash Return</strong> assuming standard financing (25% down, 7% rate).
                Properties are ranked 0–100 based on how well they match your goal.
            </div>
            <div>
                <span class="algo-tag">Cap Rate</span>
                <span class="algo-tag">NOI</span>
                <span class="algo-tag">Cash-on-Cash</span>
                <span class="algo-tag">Goal Scoring</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Navigation ──
st.info("Use the **sidebar** to navigate between modes.", icon="🧭")

# ── Footer Credits ──
st.markdown("""
<div class="footer-credits">
    <div class="footer-hackusf">Built for HackUSF 2026</div>
    <div class="footer-author">Made by Manik Jindal (Nick)</div>
</div>
""", unsafe_allow_html=True)
