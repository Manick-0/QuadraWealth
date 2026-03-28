"""
QuadraWealth — Shared UI Components
Reusable Streamlit components for consistent styling across modes.
"""
import os
import streamlit as st


def render_home_button():
    """Render a Home navigation button at the top of each page."""
    st.markdown("""
    <a href="/" target="_self" style="text-decoration:none;">
        <div style="display:inline-flex; align-items:center; gap:6px; padding:6px 16px;
            background:rgba(0,212,170,0.08); border:1px solid rgba(0,212,170,0.2);
            border-radius:10px; margin-bottom:1rem; transition:all 0.3s ease; cursor:pointer;"
            onmouseover="this.style.borderColor='rgba(0,212,170,0.5)'; this.style.background='rgba(0,212,170,0.15)';"
            onmouseout="this.style.borderColor='rgba(0,212,170,0.2)'; this.style.background='rgba(0,212,170,0.08)';">
            <span style="font-size:1rem;">🏠</span>
            <span style="color:#00D4AA; font-weight:600; font-size:0.85rem;">Home</span>
        </div>
    </a>
    """, unsafe_allow_html=True)

def setup_page(title: str, icon: str = "💎"):
    """Standard page configuration."""
    st.set_page_config(
        page_title=f"QuadraWealth — {title}",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()


def inject_custom_css():
    """Inject custom CSS for premium look & feel."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', sans-serif !important;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Premium metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1A1F2E 0%, #252B3B 100%);
        border: 1px solid rgba(0, 212, 170, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: rgba(0, 212, 170, 0.4);
        box-shadow: 0 8px 32px rgba(0, 212, 170, 0.08);
        transform: translateY(-2px);
    }

    /* Glowing header */
    .glow-header {
        background: linear-gradient(90deg, #00D4AA, #00B4D8, #00D4AA);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s ease-in-out infinite;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    @keyframes shimmer {
        0% { background-position: 0% center; }
        50% { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    /* Status badges */
    .badge-green {
        background: rgba(0, 212, 170, 0.15);
        color: #00D4AA;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-red {
        background: rgba(255, 75, 75, 0.15);
        color: #FF4B4B;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-blue {
        background: rgba(0, 180, 216, 0.15);
        color: #00B4D8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .badge-orange {
        background: rgba(255, 165, 0, 0.15);
        color: #FFA500;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    /* Sportsbook colors */
    .book-fanduel { color: #1A73E8; font-weight: 600; }
    .book-draftkings { color: #53D769; font-weight: 600; }
    .book-hardrockbet { color: #FF8C00; font-weight: 600; }

    /* Score bar */
    .score-bar {
        height: 8px;
        border-radius: 4px;
        background: rgba(255,255,255,0.1);
        overflow: hidden;
        margin-top: 4px;
    }
    .score-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 8px 20px !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0E1117 0%, #141824 100%);
        border-right: 1px solid rgba(0, 212, 170, 0.1);
    }

    /* Divider */
    .premium-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 212, 170, 0.3), transparent);
        margin: 1.5rem 0;
    }

    /* Table styling */
    .dataframe {
        border: none !important;
    }

    /* Hide Streamlit branding but KEEP sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
    }
    div[data-testid="stToolbar"] {display: none !important;}
    div[data-testid="stDecoration"] {display: none !important;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .stDeployButton {display: none !important;}
    #stDecoration {display: none !important;}
    .viewerBadge_container__r5tak {display: none !important;}
    .styles_viewerBadge__CvC9N {display: none !important;}

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0E1117; }
    ::-webkit-scrollbar-thumb { background: #00D4AA; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, delta: str = None, delta_color: str = "auto"):
    """Render a premium metric card.
    delta_color: 'auto' detects from sign, 'green' forces green, 'red' forces red.
    """
    delta_html = ""
    if delta:
        delta_str = str(delta).strip()
        # Auto-detect: positive if starts with + or contains +, negative if starts with - or contains (-
        if delta_color == "auto":
            is_positive = delta_str.startswith("+") or (not delta_str.startswith("-") and "+" in delta_str)
        elif delta_color == "green":
            is_positive = True
        elif delta_color == "red":
            is_positive = False
        else:
            is_positive = delta_str.startswith("+")

        color = "#00D4AA" if is_positive else "#FF4B4B"
        arrow = "↑" if is_positive else "↓"
        delta_html = f'<div style="color: {color}; font-size: 0.9rem; margin-top: 4px;">{arrow} {delta}</div>'

    st.markdown(f"""
    <div class="metric-card">
        <div style="color: rgba(250,250,250,0.6); font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">{label}</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #FAFAFA; margin-top: 4px;">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_score_badge(score: float, label: str = "Score"):
    """Render a score with a colored bar."""
    if score >= 75:
        color = "#00D4AA"
    elif score >= 50:
        color = "#FFD700"
    elif score >= 25:
        color = "#FFA500"
    else:
        color = "#FF4B4B"

    st.markdown(f"""
    <div style="margin: 4px 0;">
        <span style="font-size: 0.8rem; color: rgba(250,250,250,0.6);">{label}</span>
        <span style="font-size: 1.1rem; font-weight: 700; color: {color}; margin-left: 8px;">{score:.0f}</span>
        <span style="font-size: 0.8rem; color: rgba(250,250,250,0.4);">/100</span>
        <div class="score-bar">
            <div class="score-fill" style="width: {score}%; background: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_bookmaker_badge(bookmaker: str) -> str:
    """Return HTML for a bookmaker badge."""
    colors = {
        "FanDuel": ("#1A73E8", "book-fanduel"),
        "DraftKings": ("#53D769", "book-draftkings"),
        "Hard Rock Bet": ("#FF8C00", "book-hardrockbet"),
        "PrizePicks": ("#7B2FBE", "book-prizepicks"),
    }
    color, cls = colors.get(bookmaker, ("#FAFAFA", ""))
    return f'<span class="{cls}">{bookmaker}</span>'


def _get_backend_url():
    """Get backend URL from Streamlit secrets, env var, or default."""
    # 1. Streamlit Cloud secrets (secrets.toml)
    try:
        return st.secrets["BACKEND_URL"]
    except Exception:
        pass
    # 2. Environment variable
    url = os.environ.get("BACKEND_URL")
    if url:
        return url
    # 3. Default localhost
    return "http://localhost:8000"

BACKEND_URL = _get_backend_url()


def api_get(endpoint: str, params: dict = None):
    """Make a GET request to the backend API."""
    import requests
    try:
        resp = requests.get(f"{BACKEND_URL}{endpoint}", params=params, timeout=60)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"API Error: {resp.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend not running. Start with: `uvicorn backend.main:app --port 8000`")
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


def api_post(endpoint: str, params: dict = None, json_data: dict = None):
    """Make a POST request to the backend API."""
    import requests
    try:
        resp = requests.post(f"{BACKEND_URL}{endpoint}", params=params, json=json_data, timeout=60)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"API Error: {resp.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Backend not running. Start with: `uvicorn backend.main:app --port 8000`")
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None
