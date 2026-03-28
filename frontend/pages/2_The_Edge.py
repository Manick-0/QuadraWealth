"""
QuadraWealth — Mode 2: The Edge (Arbitrage & EV Betting)
Compare lines across FanDuel, DraftKings, and Hard Rock Bet.
Shows LIVE odds when API key is configured, mock data otherwise (clearly labeled).
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.components import inject_custom_css, render_metric_card, api_get

st.set_page_config(page_title="QuadraWealth — The Edge", page_icon="🎯", layout="wide")
inject_custom_css()

# ── Header ──
st.markdown('<div class="glow-header">🎯 The Edge — Arbitrage & +EV Finder</div>', unsafe_allow_html=True)
st.caption("Compare lines across FanDuel, DraftKings & Hard Rock Bet • NBA • NFL • MLB • T20 Cricket")
st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("### 🎯 Edge Settings")
    sport_filter = st.selectbox(
        "Sport",
        ["All Sports", "NBA", "NFL", "MLB", "T20 Cricket"],
    )
    bankroll = st.number_input("Bankroll ($)", value=1000, step=100)
    st.markdown("---")
    st.markdown("#### Sportsbooks")
    st.markdown("""
    <div style="margin: 8px 0;">
        <span class="book-fanduel">● FanDuel</span><br>
        <span class="book-draftkings">● DraftKings</span><br>
        <span class="book-hardrockbet">● Hard Rock Bet</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⚙️ API Key")
    st.caption("Set `ODDS_API_KEY` in `.env` for live data")

# ── Load Dashboard Data ──
with st.spinner("Scanning lines across sportsbooks..."):
    dashboard = api_get("/api/edge/dashboard")

if dashboard:
    # ── Data Source Banner ──
    source = dashboard.get("data_source", {})
    is_live = source.get("is_live", False)
    last_fetch = source.get("last_fetch")

    if is_live:
        fetch_time = ""
        if last_fetch:
            try:
                dt = datetime.fromisoformat(last_fetch.replace("Z", "+00:00"))
                fetch_time = dt.strftime("%I:%M %p ET")
            except Exception:
                fetch_time = last_fetch
        st.markdown(f"""
        <div style="background: rgba(0, 212, 170, 0.1); border: 1px solid rgba(0, 212, 170, 0.3);
                    border-radius: 12px; padding: 12px 20px; margin-bottom: 16px;
                    display: flex; align-items: center; gap: 12px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background: #00D4AA;
                        box-shadow: 0 0 8px #00D4AA; animation: pulse 2s infinite;"></div>
            <span style="color: #00D4AA; font-weight: 600; font-size: 0.95rem;">
                LIVE — Real-time odds from The Odds API
            </span>
            <span style="color: rgba(250,250,250,0.4); font-size: 0.8rem; margin-left: auto;">
                Last updated: {fetch_time}
            </span>
        </div>
        <style>@keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}</style>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(255, 165, 0, 0.1); border: 1px solid rgba(255, 165, 0, 0.3);
                    border-radius: 12px; padding: 12px 20px; margin-bottom: 16px;
                    display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 1.2rem;">📋</span>
            <span style="color: #FFA500; font-weight: 600; font-size: 0.95rem;">
                DEMO MODE — Showing sample data. Set ODDS_API_KEY in .env for live odds.
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── Summary Metrics ──
    mc1, mc2, mc3, mc4 = st.columns(4)
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

    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3 = st.tabs(["💰 Arbitrage", "📊 +EV Bets", "📋 Raw Odds"])

    # ── Helper: format game time ──
    def format_game_time(commence_time: str) -> str:
        if not commence_time:
            return ""
        try:
            dt = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
            return dt.strftime("%b %d · %I:%M %p")
        except Exception:
            return commence_time[:16]

    # ── Helper: bookmaker color ──
    def book_color(name: str) -> str:
        if "FanDuel" in name:
            return "#1A73E8"
        elif "DraftKings" in name:
            return "#53D769"
        elif "Hard Rock" in name:
            return "#FF8C00"
        return "#FAFAFA"

    # ── Tab 1: Arbitrage Opportunities ──
    with tab1:
        st.markdown("### 💰 Guaranteed Profit — Arbitrage Opportunities")
        st.caption("When the combined implied probability across books is < 100%, you can guarantee profit by betting both sides.")

        arbs = dashboard.get("arbitrage", [])
        if arbs:
            for arb in arbs:
                profit_scaled = arb["guaranteed_profit"] * (bankroll / 100)
                stake_a_scaled = arb["stake_a"] * (bankroll / 100)
                stake_b_scaled = arb["stake_b"] * (bankroll / 100)
                game_time = format_game_time(arb.get("commence_time", ""))

                odds_a = arb["odds_a"]
                odds_b = arb["odds_b"]
                # Format odds properly with +/- sign
                odds_a_str = f"+{odds_a}" if odds_a > 0 else str(odds_a)
                odds_b_str = f"+{odds_b}" if odds_b > 0 else str(odds_b)

                st.markdown(f"""
                <div class="metric-card" style="border-color: rgba(0, 212, 170, 0.3);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div>
                            <span style="font-size:1.1rem; font-weight:700; color:#FAFAFA;">🏆 {arb['event']}</span>
                            <span class="badge-orange" style="margin-left:12px;">{arb['sport']}</span>
                            <span class="badge-blue" style="margin-left:8px;">{arb['market'].upper()}</span>
                            <span style="color:rgba(250,250,250,0.35); font-size:0.8rem; margin-left:8px;">{game_time}</span>
                        </div>
                        <div style="font-size:1.4rem; font-weight:800; color:#00D4AA;">+{arb['arb_pct']:.2f}% EDGE</div>
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
                        <div style="background:rgba(0,0,0,0.2); padding:12px; border-radius:12px;">
                            <div style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Side A</div>
                            <div style="color:{book_color(arb['book_a'])}; font-weight:600; font-size:1.1rem;">{arb['book_a']}</div>
                            <div style="color:#FAFAFA; font-weight:500;">{arb['outcome_a']} @ {odds_a_str}</div>
                            <div style="color:#00D4AA; font-weight:600; margin-top:4px;">Stake: ${stake_a_scaled:.2f}</div>
                        </div>
                        <div style="background:rgba(0,0,0,0.2); padding:12px; border-radius:12px;">
                            <div style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Side B</div>
                            <div style="color:{book_color(arb['book_b'])}; font-weight:600; font-size:1.1rem;">{arb['book_b']}</div>
                            <div style="color:#FAFAFA; font-weight:500;">{arb['outcome_b']} @ {odds_b_str}</div>
                            <div style="color:#00D4AA; font-weight:600; margin-top:4px;">Stake: ${stake_b_scaled:.2f}</div>
                        </div>
                    </div>
                    <div style="text-align:center; margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.08);">
                        <span style="color:rgba(250,250,250,0.5);">Guaranteed Profit on ${bankroll:,.0f} bankroll:</span>
                        <span style="color:#00D4AA; font-weight:800; font-size:1.3rem; margin-left:8px;">${profit_scaled:.2f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
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

                odds_val = bet["odds"]
                odds_str = f"+{odds_val}" if odds_val > 0 else str(odds_val)

                st.markdown(f"""
                <div class="metric-card" style="padding:1rem 1.5rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:700; color:#FAFAFA;">{bet['event']}</span>
                            <span class="badge-orange" style="margin-left:8px;">{bet['sport']}</span>
                            <span style="color:rgba(250,250,250,0.35); font-size:0.8rem; margin-left:8px;">{game_time}</span>
                        </div>
                        <div style="font-size:1.1rem; font-weight:700; color:{ev_color};">
                            EV: +${bet['ev_per_dollar']:.3f}/$
                        </div>
                    </div>
                    <div style="display:flex; gap:24px; margin-top:8px; align-items:center; flex-wrap:wrap;">
                        <div>
                            <span style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Book:</span>
                            <span style="color:{book_color(bet['bookmaker'])}; font-weight:600; margin-left:4px;">{bet['bookmaker']}</span>
                        </div>
                        <div>
                            <span style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Pick:</span>
                            <span style="color:#FAFAFA; font-weight:500; margin-left:4px;">{bet['outcome']} @ {odds_str}</span>
                        </div>
                        <div>
                            <span style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Edge:</span>
                            <span class="badge-green" style="margin-left:4px;">+{bet['edge_pct']:.1f}%</span>
                        </div>
                        <div>
                            <span style="color:rgba(250,250,250,0.5); font-size:0.8rem;">Stake:</span>
                            <span style="color:#00D4AA; font-weight:600; margin-left:4px;">${stake_scaled:.2f}</span>
                        </div>
                    </div>
                    <div style="margin-top:6px; display:flex; gap:12px; flex-wrap:wrap;">
                        <span style="color:rgba(250,250,250,0.4); font-size:0.8rem;">Implied: {bet['implied_prob']:.1f}%</span>
                        <span style="color:rgba(250,250,250,0.4); font-size:0.8rem;">True: {bet['true_prob']:.1f}%</span>
                        <span style="color:rgba(250,250,250,0.4); font-size:0.8rem;">Market: {bet['market'].upper()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

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
            "T20 Cricket": "cricket",
        }

        selected_sport = sport_api_map.get(sport_filter)

        if selected_sport:
            odds_data = api_get(f"/api/edge/odds/{selected_sport}")
        else:
            odds_data = []
            for sport_key in ["nba", "nfl", "mlb", "cricket"]:
                result = api_get(f"/api/edge/odds/{sport_key}")
                if result:
                    odds_data.extend(result)

        if odds_data:
            for event in odds_data:
                game_time = format_game_time(event.get("commence_time", ""))
                with st.expander(f"🏟️ {event.get('away_team', '?')} @ {event.get('home_team', '?')} — {event.get('league', '')} · {game_time}"):
                    odds = event.get("odds", [])
                    if odds:
                        df = pd.DataFrame(odds)
                        # Format odds with +/- sign
                        df["line"] = df["price"].apply(lambda x: f"+{x}" if x > 0 else str(x))
                        display_cols = ["bookmaker", "market", "outcome", "line"]
                        if "point" in df.columns:
                            display_cols.append("point")
                        st.dataframe(
                            df[display_cols].sort_values(["market", "outcome", "bookmaker"]),
                            hide_index=True,
                            use_container_width=True,
                        )
        else:
            st.warning("No odds data available.", icon="⚠️")

    # ── Refresh button ──
    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)
    if st.button("🔄 Refresh Odds", type="primary", use_container_width=True):
        st.rerun()

else:
    st.error("Failed to load dashboard data. Is the backend running?")
