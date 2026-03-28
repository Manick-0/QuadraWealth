"""
QuadraWealth Betting / Edge Service
Arbitrage detection, +EV calculation, and The Odds API integration.

Pulls LIVE odds from The Odds API when ODDS_API_KEY is set.
Falls back to mock data with clear labeling when API is unavailable.
"""
import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend.config import settings


# ── Module state: track data source ──
_data_source = "mock"  # or "live"
_last_fetch_time = None
_cached_events = None
_cache_ttl_seconds = 120  # Re-fetch every 2 minutes


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
    else:
        return round(-100 / (decimal_odds - 1))


def load_mock_odds() -> list[dict]:
    """Load mock odds data from JSON file."""
    data_path = Path(__file__).parent.parent / "data" / "mock_odds.json"
    with open(data_path, "r") as f:
        data = json.load(f)
    return data.get("events", [])


def get_data_source() -> dict:
    """Return current data source metadata."""
    return {
        "source": _data_source,
        "last_fetch": _last_fetch_time.isoformat() if _last_fetch_time else None,
        "is_live": _data_source == "live",
    }


def fetch_live_odds(sport: str = None) -> list[dict]:
    """
    Fetch live odds from The Odds API.
    Falls back to mock data if API key is missing or request fails.
    Returns list of normalized event dicts.
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
                    for event in events:
                        event["sport"] = s
                        # Derive league name from sport key
                        league_map = {
                            "basketball_nba": "NBA",
                            "americanfootball_nfl": "NFL",
                            "baseball_mlb": "MLB",
                            "cricket_ipl": "T20 IPL",
                        }
                        event["league"] = league_map.get(s, s.split("_")[-1].upper())
                    all_events.extend(events)

                    # Log remaining API usage
                    remaining = resp.headers.get("x-requests-remaining", "?")
                    used = resp.headers.get("x-requests-used", "?")
                    print(f"📡 Odds API [{s}]: {len(events)} events | Quota: {used} used, {remaining} remaining")
                elif resp.status_code == 401:
                    print(f"⚠️ Odds API: Invalid API key")
                    break
                elif resp.status_code == 429:
                    print(f"⚠️ Odds API: Rate limit reached, falling back to mock")
                    break
                else:
                    print(f"⚠️ Odds API error for {s}: {resp.status_code} - {resp.text[:200]}")

            if all_events:
                _data_source = "live"
                _last_fetch_time = datetime.now(timezone.utc)
                _cached_events = all_events
                return all_events

        except requests.exceptions.Timeout:
            print("⚠️ Odds API timeout, using mock data")
        except requests.exceptions.ConnectionError:
            print("⚠️ Odds API connection error, using mock data")
        except Exception as e:
            print(f"⚠️ Odds API request failed: {e}, using mock data")

    # Fallback to mock data
    _data_source = "mock"
    _last_fetch_time = datetime.now(timezone.utc)
    events = load_mock_odds()
    _cached_events = events

    if sport:
        events = [e for e in events if e["sport"] == sport]
    return events


def _parse_event_lines(event: dict) -> list[dict]:
    """
    Parse all bookmaker lines for an event into a flat list.
    Each entry: {bookmaker, market, outcome, price, point}
    """
    lines = []
    bookmakers = event.get("bookmakers", [])

    for bm in bookmakers:
        bm_key = bm.get("key", "")
        bm_title = bm.get("title", bm_key)

        # Only include our target books
        if bm_key not in settings.ODDS_API_BOOKMAKERS:
            continue

        for market in bm.get("markets", []):
            market_key = market.get("key", "")
            for outcome in market.get("outcomes", []):
                lines.append({
                    "bookmaker": bm_title,
                    "bookmaker_key": bm_key,
                    "market": market_key,
                    "outcome": outcome.get("name", ""),
                    "price": outcome.get("price", 0),
                    "point": outcome.get("point"),
                })

    return lines


def find_arbitrage_opportunities(events: list[dict] = None) -> list[dict]:
    """
    Scan all events for arbitrage opportunities.
    Arbitrage exists when: (1/decimal_odds_A) + (1/decimal_odds_B) < 1.0
    """
    if events is None:
        events = fetch_live_odds()

    arbs = []

    for event in events:
        lines = _parse_event_lines(event)
        event_name = f"{event.get('away_team', '?')} @ {event.get('home_team', '?')}"
        commence = event.get("commence_time", "")

        # Group lines by market
        market_groups = {}
        for line in lines:
            key = (line["market"], line.get("point"))
            if key not in market_groups:
                market_groups[key] = {}

            outcome = line["outcome"]
            if outcome not in market_groups[key]:
                market_groups[key][outcome] = []
            market_groups[key][outcome].append(line)

        # Check each market for arb across books
        for (market, point), outcomes in market_groups.items():
            outcome_names = list(outcomes.keys())
            if len(outcome_names) < 2:
                continue

            # For 2-way markets (h2h, totals)
            for i, name_a in enumerate(outcome_names):
                for name_b in outcome_names[i + 1:]:
                    lines_a = outcomes[name_a]
                    lines_b = outcomes[name_b]

                    # Find best odds for each side across all books
                    for la in lines_a:
                        for lb in lines_b:
                            if la["bookmaker_key"] == lb["bookmaker_key"]:
                                continue  # Same book, skip

                            dec_a = _american_to_decimal(la["price"])
                            dec_b = _american_to_decimal(lb["price"])

                            arb_sum = (1 / dec_a) + (1 / dec_b)

                            if arb_sum < 1.0:
                                # Arbitrage found!
                                total_stake = 100
                                stake_a = total_stake * (1 / dec_a) / arb_sum
                                stake_b = total_stake * (1 / dec_b) / arb_sum
                                profit = total_stake * (1 / arb_sum - 1)

                                arbs.append({
                                    "event": event_name,
                                    "sport": event.get("league", event.get("sport", "")),
                                    "market": market,
                                    "commence_time": commence,
                                    "book_a": la["bookmaker"],
                                    "outcome_a": name_a,
                                    "odds_a": la["price"],
                                    "book_b": lb["bookmaker"],
                                    "outcome_b": name_b,
                                    "odds_b": lb["price"],
                                    "arb_pct": round((1 - arb_sum) * 100, 2),
                                    "stake_a": round(stake_a, 2),
                                    "stake_b": round(stake_b, 2),
                                    "guaranteed_profit": round(profit, 2),
                                })

    # Sort by profit margin descending
    arbs.sort(key=lambda x: x["arb_pct"], reverse=True)
    return arbs


def find_positive_ev_bets(events: list[dict] = None) -> list[dict]:
    """
    Find +EV bets by comparing each book's line to the consensus (average) line.
    The consensus acts as the 'true' probability estimate.
    """
    if events is None:
        events = fetch_live_odds()

    ev_bets = []

    for event in events:
        lines = _parse_event_lines(event)
        event_name = f"{event.get('away_team', '?')} @ {event.get('home_team', '?')}"
        commence = event.get("commence_time", "")

        # Group by market+outcome to find consensus
        market_outcome_groups = {}
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

                # EV = (true_prob * payout) - (1 - true_prob) * 1
                ev = (consensus_prob * (decimal_odds - 1)) - (1 - consensus_prob)

                if ev > 0.02:  # At least 2% edge
                    edge_pct = (consensus_prob - line_prob) / line_prob * 100

                    # Kelly criterion for recommended stake (quarter kelly for safety)
                    kelly_fraction = (consensus_prob * (decimal_odds - 1) - (1 - consensus_prob)) / (decimal_odds - 1)
                    recommended_stake = max(0, round(kelly_fraction * 25, 2))  # Quarter kelly on $100

                    ev_bets.append({
                        "event": event_name,
                        "sport": event.get("league", event.get("sport", "")),
                        "commence_time": commence,
                        "bookmaker": line["bookmaker"],
                        "market": market,
                        "outcome": outcome,
                        "odds": line["price"],
                        "implied_prob": round(line_prob * 100, 1),
                        "true_prob": round(consensus_prob * 100, 1),
                        "edge_pct": round(edge_pct, 1),
                        "ev_per_dollar": round(ev, 3),
                        "recommended_stake": recommended_stake,
                    })

    # Sort by EV descending
    ev_bets.sort(key=lambda x: x["ev_per_dollar"], reverse=True)
    return ev_bets


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
            "odds": lines,
        })

    return formatted
