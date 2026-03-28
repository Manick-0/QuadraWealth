"""
QuadraWealth — Mode 1: Stocks (Equity Manager)
RAG-powered stock recommendations with real-time market data.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.components import inject_custom_css, render_metric_card, render_score_badge, api_get, api_post, render_home_button

st.set_page_config(page_title="QuadraWealth — Stocks", page_icon="📈", layout="wide")
inject_custom_css()
render_home_button()

# ── Header ──
st.markdown('<div class="glow-header">📈 Stocks — Equity Manager</div>', unsafe_allow_html=True)
st.caption("Real-time market data • RAG-powered recommendations • Portfolio simulation")
st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ── Sidebar Controls ──
with st.sidebar:
    st.markdown("### 📈 Stock Settings")
    risk = st.select_slider(
        "Risk Tolerance",
        options=["conservative", "moderate", "aggressive"],
        value="moderate",
    )
    sectors = st.multiselect(
        "Focus Sectors",
        ["tech", "finance", "healthcare", "consumer", "energy"],
        default=["tech", "finance"],
    )
    capital = st.number_input("Capital ($)", value=50000, step=5000)

    st.markdown("---")
    analyze_ticker = st.text_input("🔍 Analyze Ticker", placeholder="e.g., AAPL").upper()

# ── Tabs ──
tab1, tab2, tab3 = st.tabs(["🌍 Market Overview", "🤖 AI Recommendations", "🔬 Stock Analysis"])

# ── Tab 1: Market Overview ──
with tab1:
    with st.spinner("Fetching market data..."):
        data = api_get("/api/stocks/market-overview")

    if data:
        # Market Indices
        st.markdown("### Market Indices")
        idx_cols = st.columns(3)
        for i, index in enumerate(data.get("indices", [])[:3]):
            with idx_cols[i]:
                delta = f"{index['change']:+.2f} ({index['change_pct']:+.2f}%)"
                render_metric_card(
                    index["name"],
                    f"${index['price']:,.2f}",
                    delta=delta,
                )

        st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

        # Top Movers
        col_gain, col_lose = st.columns(2)

        with col_gain:
            st.markdown("### 🟢 Top Gainers")
            for stock in data.get("top_gainers", []):
                with st.container():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"**{stock['ticker']}** — {stock.get('name', '')[:30]}")
                    c2.markdown(f"${stock['price']:.2f}")
                    c3.markdown(f"<span class='badge-green'>+{stock['change_pct']:.2f}%</span>", unsafe_allow_html=True)

        with col_lose:
            st.markdown("### 🔴 Top Losers")
            for stock in data.get("top_losers", []):
                with st.container():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.markdown(f"**{stock['ticker']}** — {stock.get('name', '')[:30]}")
                    c2.markdown(f"${stock['price']:.2f}")
                    c3.markdown(f"<span class='badge-red'>{stock['change_pct']:.2f}%</span>", unsafe_allow_html=True)

# ── Tab 2: AI Recommendations ──
with tab2:
    st.markdown("### 🤖 RAG-Powered Stock Recommendations")
    st.caption("Powered by ChromaDB vector search over financial news — cross-referenced with your risk profile.")

    if st.button("Generate Recommendations", type="primary", use_container_width=True):
        with st.spinner("Running RAG pipeline..."):
            recs = api_post(
                "/api/stocks/recommendations",
                params={
                    "risk_tolerance": risk,
                    "capital": capital,
                },
                json_data=sectors,
            )

        if recs:
            for i, rec in enumerate(recs):
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-size:1.4rem; font-weight:700; color:#FAFAFA;">{rec['ticker']}</span>
                                <span style="color:rgba(250,250,250,0.5); margin-left:12px;">{rec.get('name', '')}</span>
                            </div>
                            <div style="font-size:1.3rem; font-weight:700; color:#00D4AA;">${rec['price']:.2f}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        render_score_badge(rec["score"], "Recommendation Score")
                    with c2:
                        risk_colors = {"low": "badge-green", "medium": "badge-blue", "high": "badge-red"}
                        badge = risk_colors.get(rec.get("risk_level", "medium"), "badge-blue")
                        st.markdown(f"**Risk:** <span class='{badge}'>{rec.get('risk_level', 'medium').upper()}</span>", unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"**Sector:** {rec.get('sector', 'N/A')}")

                    # Signals
                    signals = rec.get("signals", [])
                    if signals:
                        signal_html = " ".join([
                            f"<span class='badge-blue'>{s.replace('_', ' ').title()}</span>"
                            for s in signals
                        ])
                        st.markdown(signal_html, unsafe_allow_html=True)

                    # Reasoning
                    with st.expander("View AI Reasoning"):
                        st.write(rec.get("reasoning", ""))

                    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)
    else:
        st.info("Click **Generate Recommendations** to run the RAG pipeline with your profile settings.", icon="🤖")

# ── Tab 3: Stock Analysis ──
with tab3:
    if analyze_ticker:
        with st.spinner(f"Analyzing {analyze_ticker}..."):
            analysis = api_get(f"/api/stocks/analyze/{analyze_ticker}")

        if analysis and "error" not in analysis:
            quote = analysis.get("quote", {})

            # Stock header
            st.markdown(f"### {quote.get('name', analyze_ticker)} ({analyze_ticker})")

            # Key metrics
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1:
                render_metric_card("Price", f"${quote.get('price', 0):,.2f}")
            with mc2:
                render_metric_card("P/E Ratio", f"{quote.get('pe_ratio', 'N/A')}")
            with mc3:
                render_metric_card("Market Cap", f"${(quote.get('market_cap', 0) or 0) / 1e9:.1f}B")
            with mc4:
                div_y = quote.get('dividend_yield')
                render_metric_card("Div Yield", f"{div_y*100:.2f}%" if div_y else "N/A")

            st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

            # Price chart
            history = analysis.get("history", {})
            if history.get("dates"):
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=history["dates"],
                    y=history["close"],
                    mode="lines",
                    fill="tozeroy",
                    line=dict(color="#00D4AA", width=2),
                    fillcolor="rgba(0, 212, 170, 0.08)",
                    name="Close Price",
                ))
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=30, b=0),
                    height=400,
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                    title=f"{analyze_ticker} — 6 Month Price History",
                )
                st.plotly_chart(fig, use_container_width=True)

            # Relevant news from RAG
            news = analysis.get("relevant_news", [])
            if news:
                st.markdown("### 📰 Related Financial News (RAG)")
                for n in news:
                    sentiment_badge = {
                        "bullish": "badge-green",
                        "bearish": "badge-red",
                        "neutral": "badge-blue",
                    }.get(n.get("sentiment", "neutral"), "badge-blue")
                    st.markdown(f"""
                    <div class="metric-card" style="padding:1rem;">
                        <span class='{sentiment_badge}'>{n.get('sentiment','').upper()}</span>
                        <span class='badge-orange' style="margin-left:8px;">{n.get('sector','')}</span>
                        <p style="margin-top:8px; color:rgba(250,250,250,0.8);">{n.get('text','')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        elif analysis:
            st.error(analysis.get("error", "Unknown error"))
    else:
        st.info("Enter a ticker symbol in the sidebar to perform a deep-dive analysis.", icon="🔍")
