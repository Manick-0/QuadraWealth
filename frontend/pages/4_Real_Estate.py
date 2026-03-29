"""
QuadraWealth — Mode 4: Real Estate
Property investment screener with cap rate & cash-on-cash analysis.
Live data from Realty Mole API. Filter by city, state, property type, price range.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import folium
from streamlit_folium import st_folium
import sys
import os

_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
if _root not in sys.path:
    sys.path.insert(0, _root)
_frontend = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
if _frontend not in sys.path:
    sys.path.insert(0, _frontend)

try:
    from frontend.components import inject_custom_css, render_metric_card, render_score_badge, api_get, render_home_button
except ImportError:
    from components import inject_custom_css, render_metric_card, render_score_badge, api_get, render_home_button

st.set_page_config(page_title="QuadraWealth — Real Estate", page_icon="🏠", layout="wide")
inject_custom_css()
render_home_button()

# ── Header ──
st.markdown('<div class="glow-header">🏠 Real Estate — Property Screener</div>', unsafe_allow_html=True)
st.caption("Live property data • Cap Rate & Cash-on-Cash analysis • Goal-based scoring")
st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ── Data source indicator ──
ds = api_get("/api/realestate/data-source")
if ds:
    source = ds.get("source", "Mock Data")
    is_live = ds.get("api_key_set", False) and ds.get("live_enabled", False)
    if is_live:
        st.markdown("""<div style="display:inline-flex; align-items:center; gap:8px; padding:4px 14px;
background:rgba(0,212,170,0.08); border:1px solid rgba(0,212,170,0.25); border-radius:20px; margin-bottom:1rem;">
<div style="width:8px; height:8px; border-radius:50%; background:#00D4AA; animation:live-pulse 1.5s infinite;"></div>
<span style="color:#00D4AA; font-size:0.85rem; font-weight:600;">LIVE — """ + source + """</span>
</div>""", unsafe_allow_html=True)
    else:
        st.info(f"📋 **{source}** — Set `RAPIDAPI_KEY` in `.env` for live Realty Mole property data.", icon="🏠")

# ── Fetch available locations for dropdowns ──
locations = api_get("/api/realestate/locations")
all_states = locations.get("states", []) if locations else []
all_cities = locations.get("all_cities", []) if locations else []
cities_by_state = locations.get("cities_by_state", {}) if locations else {}

# ── US state abbreviation list for live mode ──
US_STATES_LIST = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
]

# ── Sidebar Filters ──
with st.sidebar:
    st.markdown("### 🏠 Property Filters")

    goal = st.radio(
        "Investment Goal",
        ["cash_flow", "appreciation", "long_term"],
        format_func=lambda x: {
            "cash_flow": "💵 Rental Cash Flow",
            "appreciation": "📈 Short-Term Appreciation",
            "long_term": "🏗️ Long-Term Hold",
        }[x],
    )

    prop_type = st.selectbox(
        "Property Type",
        ["All", "SFH", "Condo", "Townhouse", "Multi-family"],
    )
    prop_type_filter = None if prop_type == "All" else prop_type

    price_range = st.slider("Price Range ($K)", 50, 1000, (100, 600), step=25)

    st.markdown("---")
    st.markdown("#### 📍 Location Filter")

    # Smart location selection: use dropdowns for known locations + free text
    is_live = ds and ds.get("api_key_set", False) and ds.get("live_enabled", False)

    # State selector — show all US states if live, else mock states
    state_options = US_STATES_LIST if is_live else all_states
    state_choice = st.selectbox(
        "State",
        ["All States"] + state_options,
        help="Filter properties by state",
    )
    state_filter = None if state_choice == "All States" else state_choice

    # City — show known cities for selected state, or allow free text
    if state_filter and state_filter in cities_by_state:
        available_cities = cities_by_state[state_filter]
        city_choice = st.selectbox(
            "City",
            ["All Cities"] + available_cities,
            help="Select a city in the chosen state",
        )
        city_filter = None if city_choice == "All Cities" else city_choice
    else:
        city_filter = st.text_input(
            "City",
            placeholder="e.g., Austin, Tampa, Phoenix",
            help="Type a city name to search",
        ).strip() or None

    st.markdown("---")

    limit = st.slider("Results Limit", 5, 50, 10)

    if is_live:
        st.markdown("""<div style="background:rgba(0,212,170,0.05); border:1px solid rgba(0,212,170,0.15);
border-radius:10px; padding:10px; margin-top:8px;">
<span style="color:#00D4AA; font-weight:600; font-size:0.8rem;">💡 Live Mode</span>
<p style="color:rgba(250,250,250,0.5); font-size:0.75rem; margin:4px 0 0;">
Select a state + city for real property listings from Realty Mole API.</p>
</div>""", unsafe_allow_html=True)

# ── Tabs ──
tab1, tab2, tab3 = st.tabs(["🔥 Hottest Properties", "🗺️ Property Map", "🔬 Property Analysis"])

# ── Tab 1: Hottest Properties ──
with tab1:
    # Build location label
    loc_parts = []
    if city_filter:
        loc_parts.append(city_filter.title())
    if state_filter:
        loc_parts.append(state_filter)
    loc_label = f" in {', '.join(loc_parts)}" if loc_parts else ""

    st.markdown(f"### 🔥 Top Properties — {goal.replace('_', ' ').title()}{loc_label}")

    params = {
        "goal": goal,
        "limit": limit,
        "min_price": price_range[0] * 1000,
        "max_price": price_range[1] * 1000,
    }
    if prop_type_filter:
        params["property_type"] = prop_type_filter
    if state_filter:
        params["state"] = state_filter
    if city_filter:
        params["city"] = city_filter

    with st.spinner("Analyzing properties..."):
        results = api_get("/api/realestate/hottest", params=params)

    if results:
        # Show data source badge for each result set
        first_prop = results[0].get("property", {}) if results else {}
        if first_prop.get("_source") == "live":
            st.success(f"📡 Showing **{len(results)}** live listings{loc_label}", icon="🏠")
        else:
            st.info(f"📋 Showing **{len(results)}** properties from curated dataset{loc_label}", icon="📊")

        for i, r in enumerate(results):
            prop = r.get("property", {})
            with st.container():
                card_html = f"""<div class="metric-card">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<span style="font-size:1.2rem; font-weight:700; color:#FAFAFA;">#{i+1} — {prop.get('address', '')}</span>
<span style="color:rgba(250,250,250,0.5); margin-left:8px;">{prop.get('city', '')}, {prop.get('state', '')}</span>
</div>
<div style="font-size:1.4rem; font-weight:800; color:#00D4AA;">${prop.get('price', 0):,.0f}</div>
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)

                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    render_score_badge(r.get("goal_score", 0), "Goal Score")
                with c2:
                    cap = r.get("cap_rate", 0)
                    cap_color = "#00D4AA" if cap > 6 else ("#FFD700" if cap > 4 else "#FF4B4B")
                    cap_html = f"""<div style="margin:4px 0;">
<span style="color:rgba(250,250,250,0.6); font-size:0.8rem;">Cap Rate</span><br>
<span style="font-size:1.3rem; font-weight:700; color:{cap_color};">{cap:.2f}%</span>
</div>"""
                    st.markdown(cap_html, unsafe_allow_html=True)
                with c3:
                    coc = r.get("cash_on_cash", 0)
                    coc_color = "#00D4AA" if coc > 5 else ("#FFD700" if coc > 0 else "#FF4B4B")
                    coc_html = f"""<div style="margin:4px 0;">
<span style="color:rgba(250,250,250,0.6); font-size:0.8rem;">Cash-on-Cash</span><br>
<span style="font-size:1.3rem; font-weight:700; color:{coc_color};">{coc:.2f}%</span>
</div>"""
                    st.markdown(coc_html, unsafe_allow_html=True)
                with c4:
                    mcf = r.get("monthly_cash_flow", 0)
                    mcf_color = "#00D4AA" if mcf > 0 else "#FF4B4B"
                    mcf_html = f"""<div style="margin:4px 0;">
<span style="color:rgba(250,250,250,0.6); font-size:0.8rem;">Monthly Cash Flow</span><br>
<span style="font-size:1.3rem; font-weight:700; color:{mcf_color};">${mcf:,.0f}</span>
</div>"""
                    st.markdown(mcf_html, unsafe_allow_html=True)
                with c5:
                    growth_html = f"""<div style="margin:4px 0;">
<span style="color:rgba(250,250,250,0.6); font-size:0.8rem;">Growth Rate</span><br>
<span style="font-size:1.3rem; font-weight:700; color:#00B4D8;">{prop.get('market_growth_rate', 0):.1f}%</span>
</div>"""
                    st.markdown(growth_html, unsafe_allow_html=True)

                # ── Full Breakdown (inline toggle) ──
                show_key = f"show_detail_{i}"
                if show_key not in st.session_state:
                    st.session_state[show_key] = False

                if st.button(f"{'▼ Hide' if st.session_state[show_key] else '▶ Show'} Full Breakdown", key=f"btn_{i}"):
                    st.session_state[show_key] = not st.session_state[show_key]

                if st.session_state[show_key]:
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        st.markdown("**Property Details**")
                        detail_html = f"""<div style="color:rgba(250,250,250,0.8); font-size:0.9rem; line-height:1.8;">
🏠 Type: {prop.get('property_type', '')}<br>
🛏️ Beds: {prop.get('bedrooms', 0)} | 🛁 Baths: {prop.get('bathrooms', 0)}<br>
📐 Sqft: {prop.get('sqft', 0):,}<br>
📅 Year Built: {prop.get('year_built', 0)}<br>
💵 Expected Rent: ${prop.get('expected_rent', 0):,.0f}/mo
</div>"""
                        st.markdown(detail_html, unsafe_allow_html=True)
                    with bc2:
                        st.markdown("**Financial Analysis**")
                        finance_html = f"""<div style="color:rgba(250,250,250,0.8); font-size:0.9rem; line-height:1.8;">
📊 NOI: ${r.get('noi', 0):,.0f}/yr<br>
💰 Down Payment (20%): ${r.get('down_payment', 0):,.0f}<br>
🏦 Mortgage: ${r.get('mortgage_payment', 0):,.0f}/mo<br>
💸 Total Expenses: ${r.get('total_monthly_expenses', 0):,.0f}/mo<br>
📈 Annual Cash Flow: ${r.get('annual_cash_flow', 0):,.0f}
</div>"""
                        st.markdown(finance_html, unsafe_allow_html=True)

                st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)
    else:
        loc_msg = f" in {', '.join(loc_parts)}" if loc_parts else ""
        st.warning(f"No properties match your filters{loc_msg}. Try broadening your search.", icon="🔍")

# ── Tab 2: Property Map ──
with tab2:
    st.markdown("### 🗺️ Property Locations")

    map_params = {}
    if state_filter:
        map_params["state"] = state_filter
    if city_filter:
        map_params["city"] = city_filter

    all_props = api_get("/api/realestate/properties", params=map_params if map_params else None)
    if all_props:
        # Determine center from data
        lats = [p["lat"] for p in all_props if p.get("lat")]
        lngs = [p["lng"] for p in all_props if p.get("lng")]
        if lats and lngs:
            center_lat = sum(lats) / len(lats)
            center_lng = sum(lngs) / len(lngs)
            zoom = 10 if city_filter else (6 if state_filter else 4)
        else:
            center_lat, center_lng, zoom = 37.0, -96.0, 4

        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom, tiles="CartoDB dark_matter")

        for prop in all_props:
            if prop.get("lat") and prop.get("lng"):
                popup_html = f"""<div style="font-family:Inter,sans-serif; min-width:200px;">
<b>{prop['address']}</b><br>
{prop['city']}, {prop['state']}<br>
<b>${prop['price']:,}</b><br>
{prop['bedrooms']}BR / {prop['bathrooms']}BA • {prop['sqft']:,} sqft<br>
Rent: ${prop['expected_rent']:,}/mo<br>
Growth: {prop['market_growth_rate']}%
</div>"""

                color = "green" if prop["market_growth_rate"] > 4.5 else (
                    "blue" if prop["market_growth_rate"] > 3.5 else "orange"
                )

                folium.CircleMarker(
                    location=[prop["lat"], prop["lng"]],
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=250),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                ).add_to(m)

        st_folium(m, width=None, height=500)

        # Legend
        legend_html = """<div style="display:flex; gap:24px; margin-top:8px;">
<span>🟢 High Growth (>4.5%)</span>
<span>🔵 Moderate Growth (3.5-4.5%)</span>
<span>🟠 Stable Growth (<3.5%)</span>
</div>"""
        st.markdown(legend_html, unsafe_allow_html=True)

# ── Tab 3: Individual Property Analysis ──
with tab3:
    st.markdown("### 🔬 Analyze Individual Property")

    property_id = st.number_input("Property ID (1-50)", min_value=1, max_value=50, value=1)
    analysis_goal = st.radio(
        "Analysis Goal",
        ["cash_flow", "appreciation", "long_term"],
        format_func=lambda x: x.replace("_", " ").title(),
        horizontal=True,
    )

    if st.button("Analyze Property", type="primary"):
        with st.spinner("Running financial analysis..."):
            result = api_get(f"/api/realestate/analyze/{property_id}", params={"goal": analysis_goal})

        if result and "error" not in result:
            prop = result.get("property", {})

            st.markdown(f"### {prop.get('address', '')} — {prop.get('city', '')}, {prop.get('state', '')}")

            # Key metrics
            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1:
                render_metric_card("Price", f"${prop.get('price', 0):,.0f}")
            with mc2:
                render_metric_card("Cap Rate", f"{result.get('cap_rate', 0):.2f}%")
            with mc3:
                render_metric_card("Cash-on-Cash", f"{result.get('cash_on_cash', 0):.2f}%")
            with mc4:
                render_metric_card("Monthly Flow", f"${result.get('monthly_cash_flow', 0):,.0f}")

            st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)
            render_score_badge(result.get("goal_score", 0), f"{analysis_goal.replace('_', ' ').title()} Score")

            # Cash flow waterfall chart
            st.markdown("### 💧 Monthly Cash Flow Waterfall")
            rent = prop.get("expected_rent", 0)
            tax_mo = prop.get("property_tax", 0) / 12
            ins_mo = prop.get("insurance", 0) / 12
            maint_mo = prop.get("maintenance_cost", 0) / 12
            hoa_mo = prop.get("hoa_fee", 0)
            mortgage = result.get("mortgage_payment", 0)
            cash_flow = result.get("monthly_cash_flow", 0)

            fig = go.Figure(go.Waterfall(
                name="Cash Flow",
                orientation="v",
                measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
                x=["Rent", "Property Tax", "Insurance", "Maintenance", "HOA", "Mortgage", "Net Cash Flow"],
                y=[rent, -tax_mo, -ins_mo, -maint_mo, -hoa_mo, -mortgage, 0],
                connector={"line": {"color": "rgba(0,212,170,0.3)"}},
                increasing={"marker": {"color": "#00D4AA"}},
                decreasing={"marker": {"color": "#FF4B4B"}},
                totals={"marker": {"color": "#00B4D8"}},
                text=[f"${rent:,.0f}", f"-${tax_mo:,.0f}", f"-${ins_mo:,.0f}",
                      f"-${maint_mo:,.0f}", f"-${hoa_mo:,.0f}", f"-${mortgage:,.0f}",
                      f"${cash_flow:,.0f}"],
                textposition="outside",
            ))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=0),
                height=400,
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                showlegend=False,
            )
            st.plotly_chart(fig, key="waterfall_chart")
        elif result:
            st.error(result.get("error", "Property not found"))
