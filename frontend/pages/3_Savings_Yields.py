"""
QuadraWealth — Mode 3: Savings & Yields
Dynamic yield finder with macro-trigger recommendations.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.components import inject_custom_css, render_metric_card, api_get, api_post, render_home_button

st.set_page_config(page_title="QuadraWealth — Savings & Yields", page_icon="🏦", layout="wide")
inject_custom_css()
render_home_button()

# ── Header ──
st.markdown('<div class="glow-header">🏦 Savings & Yields</div>', unsafe_allow_html=True)
st.caption("Dynamic yield finder • Macroeconomic triggers • Safe-haven allocation")
st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ── Sidebar — Macro Simulator ──
with st.sidebar:
    st.markdown("### 🏦 Macro Simulator")
    st.caption("Adjust indicators to simulate scenarios")

    use_custom = st.toggle("Custom Macro Scenario", value=False)

    if use_custom:
        inflation = st.slider("Inflation Rate (%)", 0.0, 8.0, 2.8, 0.1)
        fed_rate = st.slider("Fed Funds Rate (%)", 0.0, 8.0, 4.75, 0.25)
        gdp = st.slider("GDP Growth (%)", -2.0, 6.0, 1.8, 0.1)
    else:
        inflation = None
        fed_rate = None
        gdp = None

    risk = st.select_slider(
        "Risk Tolerance",
        options=["conservative", "moderate", "aggressive"],
        value="moderate",
    )

# ── Tabs ──
tab1, tab2 = st.tabs(["📊 Current Yields", "🎯 Recommended Allocation"])

# ── Tab 1: Current Yields ──
with tab1:
    data = api_get("/api/yields/current")

    if data:
        macro = data.get("macro", {})

        # Macro Dashboard
        st.markdown("### 📈 Macroeconomic Dashboard")
        mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
        with mc1:
            inf = macro.get("inflation_rate", 0)
            inf_color = "🔴" if inf > 3 else ("🟡" if inf > 2.5 else "🟢")
            render_metric_card("Inflation", f"{inf_color} {inf}%")
        with mc2:
            render_metric_card("Fed Rate", f"{macro.get('fed_funds_rate', 0)}%")
        with mc3:
            render_metric_card("GDP Growth", f"{macro.get('gdp_growth', 0)}%")
        with mc4:
            render_metric_card("Unemployment", f"{macro.get('unemployment', 0)}%")
        with mc5:
            render_metric_card("S&P P/E", f"{macro.get('sp500_pe', 0):.1f}")
        with mc6:
            render_metric_card("VIX", f"{macro.get('vix', 0):.1f}")

        st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

        # Yield Vehicles Table
        st.markdown("### 💰 Current Yield Vehicles")
        vehicles = data.get("vehicles", [])

        if vehicles:
            # Category filter
            categories = sorted(set(v.get("category", "") for v in vehicles))
            cat_labels = {
                "hysa": "🏦 HYSA",
                "tbill": "📄 T-Bills",
                "bond": "📈 Bonds",
                "gold": "🥇 Gold",
                "commodity": "🛢️ Commodities",
            }

            for cat in categories:
                cat_vehicles = [v for v in vehicles if v.get("category") == cat]
                st.markdown(f"#### {cat_labels.get(cat, cat.upper())}")

                for v in cat_vehicles:
                    risk_badge = {
                        "very_low": "badge-green",
                        "low": "badge-blue",
                        "medium": "badge-orange",
                    }.get(v.get("risk_level", "low"), "badge-blue")

                    yield_display = f"{v['current_yield']:.2f}%" if v["current_yield"] > 0 else "N/A (price appreciation)"

                    st.markdown(f"""
                    <div class="metric-card" style="padding:1rem 1.5rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-weight:700; color:#FAFAFA; font-size:1.1rem;">{v['name']}</span>
                            </div>
                            <div style="font-size:1.3rem; font-weight:800; color:#00D4AA;">{yield_display}</div>
                        </div>
                        <div style="display:flex; gap:16px; margin-top:8px;">
                            <span class="{risk_badge}">Risk: {v.get('risk_level', '').replace('_', ' ').title()}</span>
                            <span class="badge-blue">Liquidity: {v.get('liquidity', '').title()}</span>
                            <span style="color:rgba(250,250,250,0.4); font-size:0.85rem;">Min: ${v.get('min_investment', 0):,.0f}</span>
                        </div>
                        <p style="color:rgba(250,250,250,0.5); font-size:0.85rem; margin-top:6px; margin-bottom:0;">{v.get('description', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Yield comparison chart
            st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)
            st.markdown("### Yield Comparison")

            chart_data = [v for v in vehicles if v["current_yield"] > 0]
            if chart_data:
                df = pd.DataFrame(chart_data)
                fig = px.bar(
                    df,
                    x="name",
                    y="current_yield",
                    color="category",
                    color_discrete_map={
                        "hysa": "#00D4AA",
                        "tbill": "#00B4D8",
                        "bond": "#7B68EE",
                        "gold": "#FFD700",
                        "commodity": "#FF8C00",
                    },
                    labels={"current_yield": "Yield (%)", "name": ""},
                    template="plotly_dark",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=10, b=0),
                    height=350,
                    xaxis=dict(tickangle=-45),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: Recommended Allocation ──
with tab2:
    st.markdown("### 🎯 AI-Recommended Allocation")
    st.caption("Based on current macro environment and your risk profile.")

    if use_custom:
        st.info(f"📊 **Custom Scenario:** Inflation {inflation}% | Fed Rate {fed_rate}% | GDP {gdp}%", icon="🔧")

    with st.spinner("Computing optimal allocation..."):
        rec = api_post(
            "/api/yields/recommend",
            params={
                "inflation_rate": inflation,
                "fed_funds_rate": fed_rate,
                "gdp_growth": gdp,
                "risk_tolerance": risk,
            },
        )

    if rec:
        alloc = rec.get("allocations", {})
        rationale = rec.get("rationale", "")

        # Allocation Pie Chart
        col_pie, col_detail = st.columns([1, 1])

        with col_pie:
            labels = {
                "hysa": "💰 HYSA",
                "tbill": "📄 T-Bills",
                "bond": "📈 Bonds",
                "gold": "🥇 Gold",
                "commodity": "🛢️ Commodities",
            }
            fig = go.Figure(data=[go.Pie(
                labels=[labels.get(k, k) for k in alloc.keys()],
                values=list(alloc.values()),
                hole=0.5,
                marker=dict(colors=["#00D4AA", "#00B4D8", "#7B68EE", "#FFD700", "#FF8C00"]),
                textinfo="label+percent",
                textfont=dict(size=13, color="#FAFAFA"),
            )])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=10),
                height=400,
                showlegend=False,
                annotations=[dict(
                    text="<b>Allocation</b>",
                    x=0.5, y=0.5,
                    font_size=14,
                    font_color="#FAFAFA",
                    showarrow=False,
                )],
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_detail:
            st.markdown("#### Allocation Breakdown")
            for key, pct in sorted(alloc.items(), key=lambda x: x[1], reverse=True):
                color_map = {
                    "hysa": "#00D4AA",
                    "tbill": "#00B4D8",
                    "bond": "#7B68EE",
                    "gold": "#FFD700",
                    "commodity": "#FF8C00",
                }
                color = color_map.get(key, "#FAFAFA")
                st.markdown(f"""
                <div style="display:flex; align-items:center; margin:8px 0;">
                    <div style="width:14px; height:14px; border-radius:4px; background:{color}; margin-right:12px;"></div>
                    <div style="flex:1; color:#FAFAFA; font-weight:500;">{labels.get(key, key)}</div>
                    <div style="font-weight:700; color:{color}; font-size:1.1rem;">{pct:.1f}%</div>
                </div>
                <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden;">
                    <div style="height:100%; width:{pct}%; background:{color}; border-radius:3px;"></div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

        # Rationale
        st.markdown("### 💡 Recommendation Rationale")
        st.markdown(rationale)
    else:
        st.error("Failed to compute recommendation.")
