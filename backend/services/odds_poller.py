"""
QuadraWealth — Async Odds Poller
Background service that continuously fetches live odds from The Odds API
and runs arbitrage/+EV detection on every cycle.

Polls every 30s normally, every 15s when live (in-play) events exist.
Uses aiohttp for concurrent, non-blocking HTTP requests.
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Optional

import aiohttp

from backend.config import settings

logger = logging.getLogger("edge.poller")


class OddsPoller:
    """Background task that continuously polls The Odds API and detects opportunities."""

    # League display names
    LEAGUE_MAP = {
        "basketball_nba": "NBA",
        "americanfootball_nfl": "NFL",
        "baseball_mlb": "MLB",
        "icehockey_nhl": "NHL",
        "soccer_usa_mls": "MLS",
        "cricket_ipl": "T20 IPL",
    }

    def __init__(self):
        # ── State ──
        self._events: dict[str, dict] = {}          # event_id -> event data
        self._arbs: list[dict] = []                  # Detected arbitrage opps
        self._ev_bets: list[dict] = []               # Detected +EV bets
        self._lock = asyncio.Lock()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None

        # ── Metrics ──
        self._last_poll_time: Optional[datetime] = None
        self._poll_count: int = 0
        self._error_count: int = 0
        self._has_live_events: bool = False
        self._api_remaining: Optional[int] = None
        self._data_source: str = "starting"
        self._poll_duration_ms: float = 0
        self._auth_failed: bool = False  # Stop polling API on auth failure

    # ────────────────────────────── Lifecycle ──────────────────────────────

    async def start(self):
        """Start the background polling loop."""
        if self._running:
            logger.warning("Poller already running")
            return

        self._running = True
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=12),
            headers={"Accept": "application/json"},
        )
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("📡 Odds poller started (interval=%ds, live_interval=%ds)",
                     settings.ODDS_POLL_INTERVAL, settings.ODDS_POLL_LIVE_INTERVAL)

    async def stop(self):
        """Stop the background polling loop gracefully."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._session:
            await self._session.close()
        logger.info("🛑 Odds poller stopped (total polls=%d, errors=%d)",
                     self._poll_count, self._error_count)

    # ────────────────────────────── Poll Loop ──────────────────────────────

    async def _poll_loop(self):
        """Main polling loop — runs until stopped."""
        # Do an immediate first poll
        await self._do_poll()

        while self._running:
            interval = (settings.ODDS_POLL_LIVE_INTERVAL
                        if self._has_live_events
                        else settings.ODDS_POLL_INTERVAL)
            try:
                await asyncio.sleep(interval)
                if self._running:
                    await self._do_poll()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._error_count += 1
                logger.error("Poll loop error: %s", e, exc_info=True)
                await asyncio.sleep(5)  # Brief pause before retry

    async def _do_poll(self):
        """Execute a single poll cycle: fetch → detect → store."""
        t0 = time.monotonic()
        try:
            events = await self._fetch_all_sports()
            if events is not None:
                # Import detection functions here to avoid circular imports
                from backend.services.betting_service import (
                    find_arbitrage_opportunities,
                    find_positive_ev_bets,
                    detect_live_events,
                )

                # Detect live events
                self._has_live_events = detect_live_events(events)

                # Run detection
                arbs = find_arbitrage_opportunities(events)
                ev_bets = find_positive_ev_bets(events)

                # Thread-safe update
                async with self._lock:
                    self._events = {e.get("id", str(i)): e for i, e in enumerate(events)}
                    self._arbs = arbs
                    self._ev_bets = ev_bets

                arb_str = f"🔥 {len(arbs)} arbs!" if arbs else "0 arbs"
                logger.info(
                    "✅ Poll #%d: %d events | %s | %d +EV | live=%s | %.0fms",
                    self._poll_count + 1, len(events), arb_str,
                    len(ev_bets), self._has_live_events,
                    (time.monotonic() - t0) * 1000,
                )
            else:
                logger.warning("⚠️ Poll returned no data")

        except Exception as e:
            self._error_count += 1
            logger.error("Poll error: %s", e, exc_info=True)

        self._poll_count += 1
        self._last_poll_time = datetime.now(timezone.utc)
        self._poll_duration_ms = (time.monotonic() - t0) * 1000

    # ────────────────────────────── Fetching ──────────────────────────────

    async def _fetch_all_sports(self) -> Optional[list[dict]]:
        """Fetch odds for all configured sports concurrently."""
        if not settings.ODDS_API_KEY or self._auth_failed:
            self._data_source = "mock"
            from backend.services.betting_service import load_mock_odds
            return load_mock_odds()

        tasks = [self._fetch_sport(sport) for sport in settings.ODDS_API_SPORTS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_events = []
        for sport, result in zip(settings.ODDS_API_SPORTS, results):
            if isinstance(result, Exception):
                logger.error("Fetch error for %s: %s", sport, result)
                continue
            if result:
                all_events.extend(result)

        if all_events:
            self._data_source = "live"
            return all_events

        # Fallback to mock if all API calls failed
        logger.warning("All API calls failed, falling back to mock data")
        self._data_source = "mock"
        from backend.services.betting_service import load_mock_odds
        return load_mock_odds()

    async def _fetch_sport(self, sport: str) -> list[dict]:
        """Fetch odds for a single sport from The Odds API."""
        url = f"{settings.ODDS_API_BASE_URL}/sports/{sport}/odds"
        params = {
            "apiKey": settings.ODDS_API_KEY,
            "regions": settings.ODDS_API_REGIONS,
            "markets": settings.ODDS_API_MARKETS,
            "bookmakers": ",".join(settings.ODDS_API_BOOKMAKERS),
            "oddsFormat": "american",
        }

        try:
            async with self._session.get(url, params=params) as resp:
                if resp.status == 200:
                    events = await resp.json()
                    league = self.LEAGUE_MAP.get(sport, sport.split("_")[-1].upper())
                    for event in events:
                        event["sport"] = sport
                        event["league"] = league

                    # Track API quota
                    remaining = resp.headers.get("x-requests-remaining")
                    if remaining:
                        self._api_remaining = int(remaining)

                    return events

                elif resp.status == 401:
                    logger.error("Invalid API key — pausing live polling")
                    self._auth_failed = True
                    return []
                elif resp.status == 429:
                    logger.warning("Rate limited on %s — backing off", sport)
                    return []
                elif resp.status == 422:
                    # Sport not available / no events
                    return []
                else:
                    text = await resp.text()
                    logger.warning("API %d for %s: %s", resp.status, sport, text[:200])
                    return []

        except aiohttp.ClientError as e:
            logger.error("HTTP error fetching %s: %s", sport, e)
            return []

    # ────────────────────────────── Getters (thread-safe) ──────────────────

    async def get_arbs(self) -> list[dict]:
        async with self._lock:
            return list(self._arbs)

    async def get_ev_bets(self) -> list[dict]:
        async with self._lock:
            return list(self._ev_bets)

    async def get_events(self, sport: str = None) -> list[dict]:
        async with self._lock:
            events = list(self._events.values())
        if sport:
            events = [e for e in events if e.get("sport") == sport]
        return events

    async def get_status(self) -> dict:
        return {
            "is_running": self._running,
            "data_source": self._data_source,
            "is_live": self._data_source == "live",
            "last_poll": self._last_poll_time.isoformat() if self._last_poll_time else None,
            "poll_count": self._poll_count,
            "error_count": self._error_count,
            "event_count": len(self._events),
            "arb_count": len(self._arbs),
            "ev_bet_count": len(self._ev_bets),
            "has_live_events": self._has_live_events,
            "api_requests_remaining": self._api_remaining,
            "poll_duration_ms": round(self._poll_duration_ms, 1),
            "poll_interval": (settings.ODDS_POLL_LIVE_INTERVAL
                              if self._has_live_events
                              else settings.ODDS_POLL_INTERVAL),
        }

    async def get_dashboard(self) -> dict:
        """Single combined payload for the frontend dashboard."""
        async with self._lock:
            arbs = list(self._arbs)
            ev_bets = list(self._ev_bets)
            event_count = len(self._events)

        status = await self.get_status()
        return {
            "data_source": {
                "source": self._data_source,
                "is_live": self._data_source == "live",
                "last_fetch": self._last_poll_time.isoformat() if self._last_poll_time else None,
            },
            "poller": status,
            "arbitrage_count": len(arbs),
            "arbitrage": arbs[:20],
            "ev_bet_count": len(ev_bets),
            "positive_ev": ev_bets[:25],
            "total_events": event_count,
        }


# ── Module-level singleton ──
_poller: Optional[OddsPoller] = None


def get_poller() -> OddsPoller:
    """Get or create the global OddsPoller singleton."""
    global _poller
    if _poller is None:
        _poller = OddsPoller()
    return _poller
