"""
QuadraWealth — Mode 2: The Edge (Arbitrage & EV Betting) — v2.0
Real-time arbitrage scanner with auto-refresh, live event markers, and N-way arb support.
Compare lines across FanDuel, DraftKings, Hard Rock Bet, BetMGM, Caesars & PrizePicks.
"""
import streamlit as st
import pandas as pd
import time
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.components import inject_custom_css, render_metric_card, api_get, render_home_button

st.set_page_config(page_title="QuadraWealth — The Edge", page_icon="🎯", layout="wide")
inject_custom_css()
render_home_button()

# ── Header ──
st.markdown('<div class="glow-header">🎯 The Edge — Real-Time Arbitrage Scanner</div>', unsafe_allow_html=True)
st.caption("Live odds across FanDuel, DraftKings, Hard Rock Bet, BetMGM, Caesars & PrizePicks • NBA • NFL • MLB • NHL • MLS • T20 Cricket")
st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### 🎯 Edge Settings")
    sport_filter = st.selectbox(
        "Sport",
        ["All Sports", "NBA", "NFL", "MLB", "NHL", "MLS", "T20 Cricket"],
    )
    bankroll = st.number_input("Bankroll ($)", value=1000, step=100, min_value=10)

    st.markdown("---")
    st.markdown("#### 🔄 Auto-Refresh")
    auto_refresh = st.toggle("Auto-refresh", value=True)
    refresh_interval = st.select_slider(
        "Interval (seconds)",
        options=[10, 15, 20, 30, 60],
        value=15,
    )

    st.markdown("---")
    st.markdown("#### Sportsbooks")
    st.markdown("""
    <div style="margin: 8px 0; line-height: 2;">
        <span class="book-fanduel">● FanDuel</span><br>
        <span class="book-draftkings">● DraftKings</span><br>
        <span class="book-hardrockbet">● Hard Rock Bet</span><br>
        <span style="color:#C4A962; font-weight:600;">● BetMGM</span><br>
        <span style="color:#00A650; font-weight:600;">● Caesars</span><br>
        <span style="color:#7B2FBE; font-weight:600;">● PrizePicks</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⚙️ API Key")
    st.caption("Set `ODDS_API_KEY` in `.env` for live data")


# ── Helper: bookmaker color ──
def book_color(name: str) -> str:
    colors = {
        "FanDuel": "#1A73E8",
        "DraftKings": "#53D769",
        "Hard Rock Bet": "#FF8C00",
        "BetMGM": "#C4A962",
        "Caesars": "#00A650",
        "PrizePicks": "#7B2FBE",
    }
    return colors.get(name, "#FAFAFA")


# ── Helper: format game time ──
def format_game_time(commence_time: str) -> str:
    if not commence_time:
        return ""
    try:
        dt = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
        return dt.strftime("%b %d · %I:%M %p")
    except Exception:
        return commence_time[:16]


# ── Helper: format American odds with +/- ──
def fmt_odds(odds_val) -> str:
    try:
        v = float(odds_val)
        return f"+{int(v)}" if v > 0 else str(int(v))
    except (ValueError, TypeError):
        return str(odds_val)


# ── Load Dashboard Data ──
with st.spinner("Scanning lines across sportsbooks..."):
    dashboard = api_get("/api/edge/dashboard")

if dashboard:
    # ── Poller Status Bar ──
    poller = dashboard.get("poller", {})
    source = dashboard.get("data_source", {})
    is_live = source.get("is_live", False)
    last_fetch = source.get("last_fetch")
    has_live_events = poller.get("has_live_events", False)

    # Build status bar
    if is_live:
        fetch_time = ""
        if last_fetch:
            try:
                dt = datetime.fromisoformat(last_fetch.replace("Z", "+00:00"))
                fetch_time = dt.strftime("%I:%M:%S %p ET")
            except Exception:
                fetch_time = last_fetch

        poll_count = poller.get("poll_count", 0)
        poll_ms = poller.get("poll_duration_ms", 0)
        api_remaining = poller.get("api_requests_remaining")
        poll_interval = poller.get("poll_interval", 30)
        live_badge = '<span class="live-dot"></span> LIVE EVENTS' if has_live_events else ""

        status_html = f"""<div style="background: rgba(0, 212, 170, 0.08); border: 1px solid rgba(0, 212, 170, 0.25); border-radius: 12px; padding: 10px 20px; margin-bottom: 16px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
<div style="display:flex; align-items:center; gap:8px;">
<div style="width: 10px; height: 10px; border-radius: 50%; background: #00D4AA; box-shadow: 0 0 8px #00D4AA; animation: live-pulse 2s infinite;"></div>
<span style="color: #00D4AA; font-weight: 600; font-size: 0.9rem;">LIVE — Real-time odds</span>
</div>
<span style="color:rgba(250,250,250,0.35); font-size:0.78rem;">Poll #{poll_count} · {poll_ms:.0f}ms · every {poll_interval}s</span>
{f'<span style="color:rgba(250,250,250,0.35); font-size:0.78rem;">API: {api_remaining} remaining</span>' if api_remaining else ''}
<span style="color:rgba(250,250,250,0.35); font-size:0.78rem; margin-left:auto;">{fetch_time}</span>
{f'<span style="font-size:0.8rem;">{live_badge}</span>' if live_badge else ''}
</div>
<style>@keyframes live-pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}</style>"""
        st.markdown(status_html, unsafe_allow_html=True)
    else:
        demo_html = """<div style="background: rgba(255, 165, 0, 0.1); border: 1px solid rgba(255, 165, 0, 0.3); border-radius: 12px; padding: 12px 20px; margin-bottom: 16px; display: flex; align-items: center; gap: 12px;">
<span style="font-size: 1.2rem;">📋</span>
<span style="color: #FFA500; font-weight: 600; font-size: 0.95rem;">DEMO MODE — Showing sample data. Set ODDS_API_KEY in .env for live odds.</span>
</div>"""
        st.markdown(demo_html, unsafe_allow_html=True)

    # ── Summary Metrics ──
    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    with mc1:
        render_metric_card("Total Events", str(dashboard.get("total_events", 0)))
    with mc2:
        arb_count = dashboard.get("arbitrage_count", 0)
        render_metric_card(
            "Arb Opportunities",
            str(arb_count),
            delta=f"{'🔥 Live finds!' if arb_count > 0 else 'None found'}",
            delta_color="green" if arb_count > 0 else "red",
        )
    with mc3:
        render_metric_card("EV+ Bets", str(dashboard.get("ev_bet_count", 0)))
    with mc4:
        source_label = "🟢 LIVE" if is_live else "📋 DEMO"
        render_metric_card("Data Source", source_label)
    with mc5:
        sports_count = len(set(
            e.get("sport", "") for e in dashboard.get("arbitrage", [])
        ) | set(
            e.get("sport", "") for e in dashboard.get("positive_ev", [])
        )) or "—"
        render_metric_card("Sports Active", str(sports_count))

    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3 = st.tabs(["💰 Arbitrage", "📊 +EV Bets", "📋 Raw Odds"])

    # ── Tab 1: Arbitrage Opportunities ──
    with tab1:
        st.markdown("### 💰 Guaranteed Profit — Arbitrage Opportunities")
        st.caption("When the combined implied probability across books is < 100%, you can guarantee profit by betting all sides.")

        arbs = dashboard.get("arbitrage", [])
        if arbs:
            for arb in arbs:
                scale = bankroll / 100
                profit_scaled = arb["guaranteed_profit"] * scale
                game_time = format_game_time(arb.get("commence_time", ""))
                is_arb_live = arb.get("is_live", False)
                num_legs = arb.get("num_legs", 2)
                legs = arb.get("legs", [])

                # Live badge
                live_html = '<span class="live-dot"></span> <span style="color:#FF4B4B; font-weight:600; font-size:0.75rem;">LIVE</span>' if is_arb_live else ""

                # Build legs HTML
                legs_html = ""
                if legs:
                    cols = min(num_legs, 4)
                    grid_template = " ".join(["1fr"] * cols)
                    leg_cards = ""
                    for idx, leg in enumerate(legs):
                        stake_scaled = leg["stake"] * scale
                        odds_str = fmt_odds(leg["odds"])
                        bcolor = book_color(leg["book"])
                        leg_cards += f"""
                        <div style="background:rgba(0,0,0,0.2); padding:12px; border-radius:12px;">
                            <div style="color:rgba(250,250,250,0.5); font-size:0.75rem;">Leg {idx+1}</div>
                            <div style="color:{bcolor}; font-weight:600; font-size:1.05rem;">{leg['book']}</div>
                            <div style="color:#FAFAFA; font-weight:500;">{leg['outcome']} @ {odds_str}</div>
                            <div style="color:rgba(250,250,250,0.4); font-size:0.78rem; margin-top:2px;">Implied: {leg.get('implied_prob', 0):.1f}%</div>
                            <div style="color:#00D4AA; font-weight:600; margin-top:4px;">Stake: ${stake_scaled:.2f}</div>
                        </div>"""

                    legs_html = f'<div style="display:grid; grid-template-columns:{grid_template}; gap:12px;">{leg_cards}</div>'
                else:
                    # Legacy 2-way fallback
                    stake_a_scaled = arb.get("stake_a", 0) * scale
                    stake_b_scaled = arb.get("stake_b", 0) * scale
                    odds_a_str = fmt_odds(arb.get("odds_a", 0))
                    odds_b_str = fmt_odds(arb.get("odds_b", 0))

                    legs_html = f"""
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                        <div style="background:rgba(0,0,0,0.2); padding:12px; border-radius:12px;">
                            <div style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Side A</div>
                            <div style="color:{book_color(arb.get('book_a',''))}; font-weight:600; font-size:1.1rem;">{arb.get('book_a','')}</div>
                            <div style="color:#FAFAFA; font-weight:500;">{arb.get('outcome_a','')} @ {odds_a_str}</div>
                            <div style="color:#00D4AA; font-weight:600; margin-top:4px;">Stake: ${stake_a_scaled:.2f}</div>
                        </div>
                        <div style="background:rgba(0,0,0,0.2); padding:12px; border-radius:12px;">
                            <div style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Side B</div>
                            <div style="color:{book_color(arb.get('book_b',''))}; font-weight:600; font-size:1.1rem;">{arb.get('book_b','')}</div>
                            <div style="color:#FAFAFA; font-weight:500;">{arb.get('outcome_b','')} @ {odds_b_str}</div>
                            <div style="color:#00D4AA; font-weight:600; margin-top:4px;">Stake: ${stake_b_scaled:.2f}</div>
                        </div>
                    </div>"""

                # Render entire card as ONE st.markdown call
                card_html = f"""<div class="metric-card" style="border-color: rgba(0, 212, 170, 0.3);">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
<div>
<span style="font-size:1.1rem; font-weight:700; color:#FAFAFA;">🏆 {arb['event']}</span>
<span class="badge-orange" style="margin-left:12px;">{arb['sport']}</span>
<span class="badge-blue" style="margin-left:8px;">{arb['market'].upper()}</span>
{f'<span style="color:rgba(250,250,250,0.35); font-size:0.8rem; margin-left:8px;">{game_time}</span>' if game_time else ''}
{f'<span style="margin-left:8px;">{live_html}</span>' if live_html else ''}
{f'<span class="badge-green" style="margin-left:8px;">{num_legs}-WAY</span>' if num_legs > 2 else ''}
</div>
<div style="font-size:1.4rem; font-weight:800; color:#00D4AA;">+{arb['arb_pct']:.2f}% EDGE</div>
</div>
{legs_html}
<div style="text-align:center; margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.08);">
<span style="color:rgba(250,250,250,0.5);">Guaranteed Profit on ${bankroll:,.0f} bankroll:</span>
<span style="color:#00D4AA; font-weight:800; font-size:1.3rem; margin-left:8px;">${profit_scaled:.2f}</span>
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)
                st.markdown("")
        else:
            st.info("No arbitrage opportunities detected in current lines. Markets are generally efficient — check back when lines move!", icon="📊")

    # ── Tab 2: +EV Bets ──
    with tab2:
        st.markdown("### 📊 Positive Expected Value Bets")
        st.caption("Bets where the true probability (consensus across books) exceeds the implied odds — giving you a mathematical edge.")

        ev_bets = dashboard.get("positive_ev", [])
        if ev_bets:
            for bet in ev_bets:
                stake_scaled = bet["recommended_stake"] * (bankroll / 100)
                ev_color = "#00D4AA" if bet["ev_per_dollar"] > 0.05 else "#FFD700"
                game_time = format_game_time(bet.get("commence_time", ""))
                is_bet_live = bet.get("is_live", False)
                odds_str = fmt_odds(bet["odds"])
                num_books = bet.get("num_books_consensus", 0)

                live_html = '<span class="live-dot"></span>' if is_bet_live else ""

                ev_html = f"""<div class="metric-card" style="padding:1rem 1.5rem;">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
{live_html}
<span style="font-weight:700; color:#FAFAFA;">{bet['event']}</span>
<span class="badge-orange" style="margin-left:8px;">{bet['sport']}</span>
<span style="color:rgba(250,250,250,0.35); font-size:0.8rem; margin-left:8px;">{game_time}</span>
</div>
<div style="font-size:1.1rem; font-weight:700; color:{ev_color};">EV: +${bet['ev_per_dollar']:.3f}/$</div>
</div>
<div style="display:flex; gap:24px; margin-top:8px; align-items:center; flex-wrap:wrap;">
<div><span style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Book:</span> <span style="color:{book_color(bet['bookmaker'])}; font-weight:600;">{bet['bookmaker']}</span></div>
<div><span style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Pick:</span> <span style="color:#FAFAFA; font-weight:500;">{bet['outcome']} @ {odds_str}</span></div>
<div><span style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Edge:</span> <span class="badge-green" style="margin-left:4px;">+{bet['edge_pct']:.1f}%</span></div>
<div><span style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Stake:</span> <span style="color:#00D4AA; font-weight:600;">${stake_scaled:.2f}</span></div>
</div>
<div style="margin-top:6px; display:flex; gap:12px; flex-wrap:wrap;">
<span style="color:rgba(250,250,250,0.4); font-size:0.8rem;">Implied: {bet['implied_prob']:.1f}%</span>
<span style="color:rgba(250,250,250,0.4); font-size:0.8rem;">True: {bet['true_prob']:.1f}%</span>
<span style="color:rgba(250,250,250,0.4); font-size:0.8rem;">Market: {bet['market'].upper()}</span>
{f'<span style="color:rgba(250,250,250,0.4); font-size:0.8rem;">Consensus: {num_books} books</span>' if num_books else ''}
</div>
</div>"""
                st.markdown(ev_html, unsafe_allow_html=True)

        else:
            st.info("No +EV bets found at current lines.", icon="📊")

    # ── Tab 3: Raw Odds ──
    with tab3:
        st.markdown("### 📋 Raw Odds Comparison")

        sport_api_map = {
            "All Sports": None,
            "NBA": "nba",
            "NFL": "nfl",
            "MLB": "mlb",
            "NHL": "nhl",
            "MLS": "mls",
            "T20 Cricket": "cricket",
        }

        selected_sport = sport_api_map.get(sport_filter)

        if selected_sport:
            odds_data = api_get(f"/api/edge/odds/{selected_sport}")
        else:
            odds_data = []
            for sport_key in ["nba", "nfl", "mlb", "nhl", "mls", "cricket"]:
                result = api_get(f"/api/edge/odds/{sport_key}")
                if result:
                    odds_data.extend(result)

        if odds_data:
            for event in odds_data:
                game_time = format_game_time(event.get("commence_time", ""))
                is_evt_live = event.get("is_live", False)
                live_icon = "🔴 " if is_evt_live else "🏟️ "
                with st.expander(f"{live_icon}{event.get('away_team', '?')} @ {event.get('home_team', '?')} — {event.get('league', '')} · {game_time}"):
                    odds = event.get("odds", [])
                    if odds:
                        df = pd.DataFrame(odds)
                        # Format odds with +/- sign
                        df["line"] = df["price"].apply(lambda x: f"+{int(x)}" if x > 0 else str(int(x)))
                        display_cols = ["bookmaker", "market", "outcome", "line"]
                        if "point" in df.columns:
                            display_cols.append("point")
                        st.dataframe(
                            df[display_cols].sort_values(["market", "outcome", "bookmaker"]),
                            hide_index=True,
                            width='stretch',
                        )
        else:
            st.warning("No odds data available.", icon="⚠️")

    # ── Footer ──
    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

    col_refresh, col_status = st.columns([1, 1])
    with col_refresh:
        if st.button("🔄 Refresh Now", type="primary"):
            st.rerun()
    with col_status:
        if poller.get("is_running"):
            interval = poller.get("poll_interval", 30)
            st.caption(f"⚡ Poller active — scanning every {interval}s")
        else:
            st.caption("⏸️ Poller inactive — using on-demand fetch")

    # ── Auto-refresh ──
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

else:
    st.error("Failed to load dashboard data. Is the backend running?")
    st.code("uvicorn backend.main:app --port 8000", language="bash")
