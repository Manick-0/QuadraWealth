"""
QuadraWealth Edge (Betting) Router — v2.0
API endpoints for real-time arbitrage detection and +EV bet finding.

Reads from the background OddsPoller for instant responses.
Includes SSE streaming endpoint for real-time frontend updates.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from typing import Optional

from backend.services.odds_poller import get_poller
from backend.services.betting_service import (
    find_arbitrage_opportunities,
    find_positive_ev_bets,
    get_odds_by_sport,
    fetch_live_odds,
    get_data_source,
)

logger = logging.getLogger("edge.router")
router = APIRouter()

SPORT_MAP = {
    "nba": "basketball_nba",
    "nfl": "americanfootball_nfl",
    "mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
    "mls": "soccer_usa_mls",
    "cricket": "cricket_ipl",
}


@router.get("/arbitrage")
async def get_arbitrage():
    """Find all current arbitrage opportunities across sportsbooks."""
    poller = get_poller()
    if poller._running:
        return await poller.get_arbs()
    return find_arbitrage_opportunities()


@router.get("/positive-ev")
async def get_positive_ev():
    """Find all current +EV betting opportunities."""
    poller = get_poller()
    if poller._running:
        return await poller.get_ev_bets()
    return find_positive_ev_bets()


@router.get("/odds/{sport}")
async def get_odds(sport: str):
    """Get odds for a specific sport (nba, nfl, mlb, nhl, mls, cricket)."""
    sport_key = SPORT_MAP.get(sport.lower(), sport)
    poller = get_poller()

    if poller._running:
        events = await poller.get_events(sport=sport_key)
        from backend.services.betting_service import _parse_event_lines, _is_event_live
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

    return get_odds_by_sport(sport_key)


@router.get("/sports")
async def list_sports():
    """List available sports."""
    return {
        "sports": [
            {"key": "nba", "name": "NBA Basketball", "api_key": "basketball_nba"},
            {"key": "nfl", "name": "NFL Football", "api_key": "americanfootball_nfl"},
            {"key": "mlb", "name": "MLB Baseball", "api_key": "baseball_mlb"},
            {"key": "nhl", "name": "NHL Hockey", "api_key": "icehockey_nhl"},
            {"key": "mls", "name": "MLS Soccer", "api_key": "soccer_usa_mls"},
            {"key": "cricket", "name": "T20 Cricket (IPL)", "api_key": "cricket_ipl"},
        ]
    }


@router.get("/source")
async def data_source():
    """Check whether data is live or mock."""
    poller = get_poller()
    if poller._running:
        status = await poller.get_status()
        return {
            "source": status["data_source"],
            "is_live": status["is_live"],
            "last_fetch": status["last_poll"],
        }
    return get_data_source()


@router.get("/status")
async def poller_status():
    """Detailed poller health and metrics."""
    poller = get_poller()
    return await poller.get_status()


@router.get("/dashboard")
async def edge_dashboard():
    """
    Combined dashboard data: arbitrage + top EV bets + data source info.
    Single endpoint for the frontend to load everything.
    """
    poller = get_poller()
    if poller._running:
        return await poller.get_dashboard()

    # Fallback: direct fetch (poller not running)
    events = fetch_live_odds()
    arbs = find_arbitrage_opportunities(events)
    ev_bets = find_positive_ev_bets(events)
    source = get_data_source()

    return {
        "data_source": source,
        "poller": {"is_running": False},
        "arbitrage_count": len(arbs),
        "arbitrage": arbs[:20],
        "ev_bet_count": len(ev_bets),
        "positive_ev": ev_bets[:25],
        "total_events": len(events),
    }


@router.get("/stream")
async def stream_updates(request: Request):
    """
    Server-Sent Events (SSE) endpoint for real-time dashboard updates.
    Frontend connects once and receives updates every poll cycle.
    """
    async def event_generator():
        poller = get_poller()
        last_poll_count = 0

        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break

            status = await poller.get_status()
            current_poll_count = status.get("poll_count", 0)

            # Only send when new data is available
            if current_poll_count != last_poll_count:
                dashboard = await poller.get_dashboard()
                data = json.dumps(dashboard, default=str)
                yield f"data: {data}\n\n"
                last_poll_count = current_poll_count

            await asyncio.sleep(2)  # Check every 2s

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
