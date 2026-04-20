from __future__ import annotations
"""
QuadraWealth Betting / Edge Service — v2.0
Optimized arbitrage detection, +EV calculation, and The Odds API integration.

Key improvements over v1:
- Optimized arb detection: finds best odds per side, then checks (O(n) per market)
- N-way arb support: handles 3+ outcome markets (soccer moneyline w/ draw)
- Live event detection via commence_time comparison
- Deduplication: keeps highest-profit arb per event+market
- Structured logging (no more print())
- Configurable thresholds from settings
"""
import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend.config import settings

logger = logging.getLogger("edge.service")


# ── Module state (legacy compat — poller is the new primary) ──
_data_source = "mock"
_last_fetch_time = None
_cached_events = None
_cache_ttl_seconds = 60


# ═══════════════════════════════════════════════════════════════
#  ODDS CONVERSION — verified correct
# ═══════════════════════════════════════════════════════════════

def _american_to_decimal(american: float) -> float:
    """Convert American odds to decimal odds."""
    if american > 0:
        return (american / 100) + 1
    else:
        return (100 / abs(american)) + 1


def _american_to_implied_prob(american: float) -> float:
    """Convert American odds to implied probability (0-1)."""
    if american > 0:
        return 100 / (american + 100)
    else:
        return abs(american) / (abs(american) + 100)


def _decimal_to_american(decimal_odds: float) -> float:
    """Convert decimal odds to American odds."""
    if decimal_odds >= 2.0:
        return round((decimal_odds - 1) * 100)
    elif decimal_odds > 1.0:
        return round(-100 / (decimal_odds - 1))
    else:
        return 100  # Even money fallback


# ═══════════════════════════════════════════════════════════════
#  DATA LOADING
# ═══════════════════════════════════════════════════════════════

def load_mock_odds() -> list[dict]:
    """Load mock odds data from JSON file."""
    data_path = Path(__file__).parent.parent / "data" / "mock_odds.json"
    with open(data_path, "r") as f:
        data = json.load(f)
    return data.get("events", [])


def get_data_source() -> dict:
    """Return current data source metadata (legacy compat)."""
    return {
        "source": _data_source,
        "last_fetch": _last_fetch_time.isoformat() if _last_fetch_time else None,
        "is_live": _data_source == "live",
    }


def detect_live_events(events: list[dict]) -> bool:
    """Check if any events are currently in-play (live)."""
    now = datetime.now(timezone.utc)
    for event in events:
        commence = event.get("commence_time", "")
        if commence:
            try:
                ct = datetime.fromisoformat(commence.replace("Z", "+00:00"))
                if ct <= now:
                    return True
            except (ValueError, TypeError):
                continue
    return False


def _is_event_live(event: dict) -> bool:
    """Check if a single event is currently in-play."""
    now = datetime.now(timezone.utc)
    commence = event.get("commence_time", "")
    if commence:
        try:
            ct = datetime.fromisoformat(commence.replace("Z", "+00:00"))
            return ct <= now
        except (ValueError, TypeError):
            pass
    return False


def fetch_live_odds(sport: str = None) -> list[dict]:
    """
    Fetch live odds from The Odds API (synchronous fallback for non-poller use).
    The poller uses aiohttp instead — this is kept for backward compatibility.
    """
    global _data_source, _last_fetch_time, _cached_events

    # Check cache first
    if _cached_events is not None and _last_fetch_time is not None:
        age = (datetime.now(timezone.utc) - _last_fetch_time).total_seconds()
        if age < _cache_ttl_seconds:
            events = _cached_events
            if sport:
                events = [e for e in events if e.get("sport") == sport]
            return events

    # Try live API if key is provided
    if settings.ODDS_API_KEY:
        try:
            sports_to_fetch = [sport] if sport else settings.ODDS_API_SPORTS
            all_events = []

            for s in sports_to_fetch:
                url = f"{settings.ODDS_API_BASE_URL}/sports/{s}/odds"
                params = {
                    "apiKey": settings.ODDS_API_KEY,
                    "regions": settings.ODDS_API_REGIONS,
                    "markets": settings.ODDS_API_MARKETS,
                    "bookmakers": ",".join(settings.ODDS_API_BOOKMAKERS),
                    "oddsFormat": "american",
                }
                resp = requests.get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    events = resp.json()
                    league_map = {
                        "basketball_nba": "NBA",
                        "americanfootball_nfl": "NFL",
                        "baseball_mlb": "MLB",
                        "icehockey_nhl": "NHL",
                        "soccer_usa_mls": "MLS",
                        "cricket_ipl": "T20 IPL",
                    }
                    for event in events:
                        event["sport"] = s
                        event["league"] = league_map.get(s, s.split("_")[-1].upper())
                    all_events.extend(events)

                    remaining = resp.headers.get("x-requests-remaining", "?")
                    used = resp.headers.get("x-requests-used", "?")
                    logger.info("📡 Odds API [%s]: %d events | Quota: %s used, %s remaining",
                                s, len(events), used, remaining)
                elif resp.status_code == 401:
                    logger.error("Odds API: Invalid API key")
                    break
                elif resp.status_code == 429:
                    logger.warning("Odds API: Rate limit reached")
                    break
                else:
                    logger.warning("Odds API error for %s: %d - %s", s, resp.status_code, resp.text[:200])

            if all_events:
                _data_source = "live"
                _last_fetch_time = datetime.now(timezone.utc)
                _cached_events = all_events
                return all_events

        except requests.exceptions.Timeout:
            logger.warning("Odds API timeout, using mock data")
        except requests.exceptions.ConnectionError:
            logger.warning("Odds API connection error, using mock data")
        except Exception as e:
            logger.error("Odds API request failed: %s", e)

    # Fallback to mock data
    _data_source = "mock"
    _last_fetch_time = datetime.now(timezone.utc)
    events = load_mock_odds()
    _cached_events = events

    if sport:
        events = [e for e in events if e["sport"] == sport]
    return events


# ═══════════════════════════════════════════════════════════════
#  EVENT PARSING
# ═══════════════════════════════════════════════════════════════

def _parse_event_lines(event: dict) -> list[dict]:
    """
    Parse all bookmaker lines for an event into a flat list.
    Each entry: {bookmaker, bookmaker_key, market, outcome, price, point}
    """
    lines = []
    bookmakers = event.get("bookmakers", [])

    for bm in bookmakers:
        bm_key = bm.get("key", "")
        bm_title = bm.get("title", bm_key)

        # Only include configured books
        if bm_key not in settings.ODDS_API_BOOKMAKERS:
            continue

        for market in bm.get("markets", []):
            market_key = market.get("key", "")
            for outcome in market.get("outcomes", []):
                price = outcome.get("price", 0)
                if price == 0:
                    continue  # Skip invalid odds

                lines.append({
                    "bookmaker": bm_title,
                    "bookmaker_key": bm_key,
                    "market": market_key,
                    "outcome": outcome.get("name", ""),
                    "price": price,
                    "point": outcome.get("point"),
                })

    return lines


# ═══════════════════════════════════════════════════════════════
#  ARBITRAGE DETECTION — v2 (optimized, N-way)
# ═══════════════════════════════════════════════════════════════

def find_arbitrage_opportunities(events: list[dict] = None) -> list[dict]:
    """
    Scan all events for arbitrage opportunities.

    v2 improvements:
    - Finds best odds per outcome across all books FIRST, then checks arb (O(n) per market)
    - Supports N-way markets (soccer: home/draw/away)
    - Deduplicates — keeps highest-profit arb per event+market
    - Filters by configurable minimum profit threshold
    """
    if events is None:
        events = fetch_live_odds()

    arbs = []
    seen = set()  # Dedup key: (event_id, market, point)

    for event in events:
        lines = _parse_event_lines(event)
        if not lines:
            continue

        event_id = event.get("id", "")
        event_name = f"{event.get('away_team', '?')} @ {event.get('home_team', '?')}"
        commence = event.get("commence_time", "")
        is_live = _is_event_live(event)

        # Group lines by (market, point)
        market_groups: dict[tuple, dict[str, list[dict]]] = {}
        for line in lines:
            key = (line["market"], line.get("point"))
            if key not in market_groups:
                market_groups[key] = {}

            outcome = line["outcome"]
            if outcome not in market_groups[key]:
                market_groups[key][outcome] = []
            market_groups[key][outcome].append(line)

        # For each market, find best odds per outcome across all books
        for (market, point), outcomes in market_groups.items():
            outcome_names = list(outcomes.keys())
            if len(outcome_names) < 2:
                continue

            # ── N-way arb check: find best odds for EACH outcome ──
            best_per_outcome: list[dict] = []
            for name in outcome_names:
                lines_for_outcome = outcomes[name]
                # Find the line with highest decimal odds (best payout)
                best = max(lines_for_outcome, key=lambda l: _american_to_decimal(l["price"]))
                best_per_outcome.append(best)

            # Calculate arb sum using best odds from each side
            decimal_odds = [_american_to_decimal(b["price"]) for b in best_per_outcome]
            arb_sum = sum(1 / d for d in decimal_odds)

            if arb_sum < 1.0 and (1 - arb_sum) * 100 >= settings.ARB_MIN_PROFIT_PCT:
                # ── Arb found! Calculate optimal stakes ──
                total_stake = 100
                stakes = [total_stake * (1 / d) / arb_sum for d in decimal_odds]
                profit = total_stake * (1 / arb_sum - 1)
                arb_pct = (1 - arb_sum) * 100

                # Dedup: keep highest profit per event+market
                dedup_key = (event_id, market, point)
                if dedup_key in seen:
                    # Find existing and replace if this is better
                    for i, existing in enumerate(arbs):
                        if (existing.get("_dedup_key") == dedup_key and
                                arb_pct > existing["arb_pct"]):
                            arbs[i] = None  # Mark for removal
                            break
                seen.add(dedup_key)

                # Build legs list for N-way display
                legs = []
                for j, best in enumerate(best_per_outcome):
                    legs.append({
                        "book": best["bookmaker"],
                        "book_key": best["bookmaker_key"],
                        "outcome": outcome_names[j],
                        "odds": best["price"],
                        "decimal_odds": round(decimal_odds[j], 4),
                        "implied_prob": round((1 / decimal_odds[j]) * 100, 2),
                        "stake": round(stakes[j], 2),
                    })

                arb_entry = {
                    "event": event_name,
                    "event_id": event_id,
                    "sport": event.get("league", event.get("sport", "")),
                    "market": market,
                    "point": point,
                    "commence_time": commence,
                    "is_live": is_live,
                    "legs": legs,
                    "num_legs": len(legs),
                    "arb_pct": round(arb_pct, 3),
                    "arb_sum": round(arb_sum, 5),
                    "guaranteed_profit": round(profit, 2),
                    # Legacy compat fields (for 2-way arbs)
                    "book_a": legs[0]["book"],
                    "outcome_a": legs[0]["outcome"],
                    "odds_a": legs[0]["odds"],
                    "stake_a": legs[0]["stake"],
                    "book_b": legs[1]["book"] if len(legs) > 1 else "",
                    "outcome_b": legs[1]["outcome"] if len(legs) > 1 else "",
                    "odds_b": legs[1]["odds"] if len(legs) > 1 else 0,
                    "stake_b": legs[1]["stake"] if len(legs) > 1 else 0,
                    "_dedup_key": (event_id, market, point),
                }
                arbs.append(arb_entry)

    # Clean up deduped entries and internal keys
    arbs = [a for a in arbs if a is not None]
    for a in arbs:
        a.pop("_dedup_key", None)

    # Sort by profit margin descending
    arbs.sort(key=lambda x: x["arb_pct"], reverse=True)
    return arbs


# ═══════════════════════════════════════════════════════════════
#  POSITIVE EV DETECTION
# ═══════════════════════════════════════════════════════════════

def find_positive_ev_bets(events: list[dict] = None) -> list[dict]:
    """
    Find +EV bets by comparing each book's line to the consensus (average) line.
    The consensus acts as the 'true' probability estimate.

    v2: Uses configurable edge threshold, better Kelly sizing.
    """
    if events is None:
        events = fetch_live_odds()

    ev_bets = []

    for event in events:
        lines = _parse_event_lines(event)
        if not lines:
            continue

        event_name = f"{event.get('away_team', '?')} @ {event.get('home_team', '?')}"
        commence = event.get("commence_time", "")
        is_live = _is_event_live(event)

        # Group by market+outcome to find consensus
        market_outcome_groups: dict[tuple, list[dict]] = {}
        for line in lines:
            key = (line["market"], line["outcome"], line.get("point"))
            if key not in market_outcome_groups:
                market_outcome_groups[key] = []
            market_outcome_groups[key].append(line)

        for (market, outcome, point), group_lines in market_outcome_groups.items():
            if len(group_lines) < 2:
                continue

            # Calculate consensus implied probability (average across books)
            implied_probs = [_american_to_implied_prob(l["price"]) for l in group_lines]
            consensus_prob = sum(implied_probs) / len(implied_probs)

            # Check each book against consensus
            for line in group_lines:
                line_prob = _american_to_implied_prob(line["price"])
                decimal_odds = _american_to_decimal(line["price"])

                # EV = (true_prob × payout) - (1 - true_prob) × stake
                ev = (consensus_prob * (decimal_odds - 1)) - (1 - consensus_prob)

                # Edge percentage
                edge_pct = (consensus_prob - line_prob) / line_prob * 100

                if ev > 0.02 and edge_pct >= settings.EV_MIN_EDGE_PCT:
                    # Kelly criterion for recommended stake (quarter kelly for safety)
                    kelly_fraction = (consensus_prob * (decimal_odds - 1) - (1 - consensus_prob)) / (decimal_odds - 1)
                    recommended_stake = max(0, round(kelly_fraction * 25, 2))  # Quarter kelly on $100

                    ev_bets.append({
                        "event": event_name,
                        "sport": event.get("league", event.get("sport", "")),
                        "commence_time": commence,
                        "is_live": is_live,
                        "bookmaker": line["bookmaker"],
                        "bookmaker_key": line["bookmaker_key"],
                        "market": market,
                        "outcome": outcome,
                        "point": point,
                        "odds": line["price"],
                        "decimal_odds": round(decimal_odds, 4),
                        "implied_prob": round(line_prob * 100, 1),
                        "true_prob": round(consensus_prob * 100, 1),
                        "edge_pct": round(edge_pct, 1),
                        "ev_per_dollar": round(ev, 3),
                        "recommended_stake": recommended_stake,
                        "num_books_consensus": len(group_lines),
                    })

    # Sort by EV descending
    ev_bets.sort(key=lambda x: x["ev_per_dollar"], reverse=True)
    return ev_bets


# ═══════════════════════════════════════════════════════════════
#  ODDS BY SPORT (for Raw Odds tab)
# ═══════════════════════════════════════════════════════════════

def get_odds_by_sport(sport: str) -> list[dict]:
    """Return all events and odds for a specific sport."""
    events = fetch_live_odds(sport=sport)

    formatted = []
    for event in events:
        lines = _parse_event_lines(event)
        formatted.append({
            "id": event.get("id", ""),
            "sport": event.get("sport", ""),
            "league": event.get("league", ""),
            "home_team": event.get("home_team", ""),
            "away_team": event.get("away_team", ""),
            "commence_time": event.get("commence_time", ""),
            "is_live": _is_event_live(event),
            "odds": lines,
        })

    return formatted
