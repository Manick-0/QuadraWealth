"""
QuadraWealth Edge (Betting) Router
API endpoints for arbitrage detection and +EV bet finding.
"""
from fastapi import APIRouter, Query
from typing import Optional

from backend.services.betting_service import (
    find_arbitrage_opportunities,
    find_positive_ev_bets,
    get_odds_by_sport,
    fetch_live_odds,
    get_data_source,
)

router = APIRouter()

SPORT_MAP = {
    "nba": "basketball_nba",
    "nfl": "americanfootball_nfl",
    "mlb": "baseball_mlb",
    "cricket": "cricket_ipl",
}


@router.get("/arbitrage")
async def get_arbitrage():
    """Find all current arbitrage opportunities across sportsbooks."""
    return find_arbitrage_opportunities()


@router.get("/positive-ev")
async def get_positive_ev():
    """Find all current +EV betting opportunities."""
    return find_positive_ev_bets()


@router.get("/odds/{sport}")
async def get_odds(sport: str):
    """Get odds for a specific sport (nba, nfl, mlb, cricket)."""
    sport_key = SPORT_MAP.get(sport.lower(), sport)
    return get_odds_by_sport(sport_key)


@router.get("/sports")
async def list_sports():
    """List available sports."""
    return {
        "sports": [
            {"key": "nba", "name": "NBA Basketball", "api_key": "basketball_nba"},
            {"key": "nfl", "name": "NFL Football", "api_key": "americanfootball_nfl"},
            {"key": "mlb", "name": "MLB Baseball", "api_key": "baseball_mlb"},
            {"key": "cricket", "name": "T20 Cricket (IPL)", "api_key": "cricket_ipl"},
        ]
    }


@router.get("/source")
async def data_source():
    """Check whether data is live or mock."""
    return get_data_source()


@router.get("/dashboard")
async def edge_dashboard():
    """
    Combined dashboard data: arbitrage + top EV bets + data source info.
    Single endpoint for the frontend to load everything.
    """
    events = fetch_live_odds()
    arbs = find_arbitrage_opportunities(events)
    ev_bets = find_positive_ev_bets(events)
    source = get_data_source()

    return {
        "data_source": source,
        "arbitrage_count": len(arbs),
        "arbitrage": arbs[:10],  # Top 10
        "ev_bet_count": len(ev_bets),
        "positive_ev": ev_bets[:15],  # Top 15
        "total_events": len(events),
    }
