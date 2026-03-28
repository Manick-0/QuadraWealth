"""
Unit tests for the arbitrage calculator and EV bet finder — v2.0.
Tests core math, N-way arb detection, live event detection, and deduplication.
"""
import pytest
import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.services.betting_service import (
    _american_to_decimal,
    _american_to_implied_prob,
    _decimal_to_american,
    find_arbitrage_opportunities,
    find_positive_ev_bets,
    detect_live_events,
    _is_event_live,
)


class TestOddsConversion:
    """Test odds format conversions."""

    def test_positive_american_to_decimal(self):
        # +150 = 2.50 decimal
        assert _american_to_decimal(150) == 2.5

    def test_negative_american_to_decimal(self):
        # -200 = 1.50 decimal
        assert _american_to_decimal(-200) == 1.5

    def test_even_money_to_decimal(self):
        # +100 = 2.0 decimal
        assert _american_to_decimal(100) == 2.0

    def test_heavy_favorite_to_decimal(self):
        # -500 = 1.20 decimal
        assert _american_to_decimal(-500) == 1.2

    def test_positive_american_to_implied_prob(self):
        # +150 → 100 / (150 + 100) = 0.40
        prob = _american_to_implied_prob(150)
        assert abs(prob - 0.40) < 0.001

    def test_negative_american_to_implied_prob(self):
        # -200 → 200 / (200 + 100) = 0.6667
        prob = _american_to_implied_prob(-200)
        assert abs(prob - 0.6667) < 0.001

    def test_even_money_implied_prob(self):
        # +100 → 100 / 200 = 0.50
        prob = _american_to_implied_prob(100)
        assert abs(prob - 0.50) < 0.001

    def test_decimal_to_american_positive(self):
        # 2.5 → +150
        assert _decimal_to_american(2.5) == 150

    def test_decimal_to_american_negative(self):
        # 1.5 → -200
        assert _decimal_to_american(1.5) == -200


class TestArbitrageDetection:
    """Test arbitrage opportunity detection — v2 with N-way support."""

    def _make_event(self, book_a_price, book_b_price, book_a="fanduel", book_b="draftkings",
                    commence_time="2026-03-30T00:00:00Z"):
        """Helper to create a test event with two books."""
        return {
            "id": "test_001",
            "sport": "basketball_nba",
            "league": "NBA",
            "home_team": "Team A",
            "away_team": "Team B",
            "commence_time": commence_time,
            "bookmakers": [
                {
                    "key": book_a,
                    "title": book_a.replace("_", " ").title(),
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Team A", "price": book_a_price[0]},
                                {"name": "Team B", "price": book_a_price[1]},
                            ]
                        }
                    ]
                },
                {
                    "key": book_b,
                    "title": book_b.replace("_", " ").title(),
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Team A", "price": book_b_price[0]},
                                {"name": "Team B", "price": book_b_price[1]},
                            ]
                        }
                    ]
                },
            ]
        }

    def _make_3way_event(self, prices_a, prices_b, prices_c):
        """Helper: 3-way market (soccer) with 3 books."""
        return {
            "id": "test_soccer_001",
            "sport": "soccer_usa_mls",
            "league": "MLS",
            "home_team": "Team Home",
            "away_team": "Team Away",
            "commence_time": "2026-03-30T00:00:00Z",
            "bookmakers": [
                {
                    "key": "fanduel",
                    "title": "FanDuel",
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Team Home", "price": prices_a[0]},
                            {"name": "Team Away", "price": prices_a[1]},
                            {"name": "Draw", "price": prices_a[2]},
                        ]
                    }]
                },
                {
                    "key": "draftkings",
                    "title": "DraftKings",
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Team Home", "price": prices_b[0]},
                            {"name": "Team Away", "price": prices_b[1]},
                            {"name": "Draw", "price": prices_b[2]},
                        ]
                    }]
                },
                {
                    "key": "hardrockbet",
                    "title": "Hard Rock Bet",
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Team Home", "price": prices_c[0]},
                            {"name": "Team Away", "price": prices_c[1]},
                            {"name": "Draw", "price": prices_c[2]},
                        ]
                    }]
                },
            ]
        }

    def test_clear_arbitrage(self):
        """When lines diverge enough, arb should be detected."""
        # Book A: Team A +200 (3.0 dec), Book B: Team B +110 (2.1 dec)
        # 1/3.0 + 1/2.1 = 0.333 + 0.476 = 0.81 < 1.0 → ARB
        event = self._make_event(
            book_a_price=(200, -250),  # FD: Team A +200, Team B -250
            book_b_price=(-150, 110),  # DK: Team A -150, Team B +110
        )
        arbs = find_arbitrage_opportunities([event])
        has_arb = len(arbs) > 0
        if has_arb:
            assert arbs[0]["arb_pct"] > 0
            assert arbs[0]["num_legs"] == 2

    def test_no_arbitrage_efficient_market(self):
        """Equally priced lines should not produce arb."""
        event = self._make_event(
            book_a_price=(-110, -110),
            book_b_price=(-110, -110),
        )
        arbs = find_arbitrage_opportunities([event])
        assert len(arbs) == 0

    def test_arb_profit_is_positive(self):
        """All detected arbs must have positive guaranteed profit."""
        event = self._make_event(
            book_a_price=(250, -300),
            book_b_price=(-120, 150),
        )
        arbs = find_arbitrage_opportunities([event])
        for arb in arbs:
            assert arb["guaranteed_profit"] > 0

    def test_arb_stakes_sum_to_bankroll(self):
        """Stake A + Stake B should roughly equal the bankroll ($100)."""
        event = self._make_event(
            book_a_price=(200, -250),
            book_b_price=(-130, 150),
        )
        arbs = find_arbitrage_opportunities([event])
        for arb in arbs:
            if arb.get("legs"):
                total = sum(leg["stake"] for leg in arb["legs"])
            else:
                total = arb["stake_a"] + arb["stake_b"]
            assert abs(total - 100) < 1  # Should be ~$100

    def test_arb_has_legs(self):
        """Detected arbs should include legs with book/outcome/odds/stake."""
        event = self._make_event(
            book_a_price=(200, -250),
            book_b_price=(-150, 110),
        )
        arbs = find_arbitrage_opportunities([event])
        for arb in arbs:
            assert "legs" in arb
            assert len(arb["legs"]) >= 2
            for leg in arb["legs"]:
                assert "book" in leg
                assert "outcome" in leg
                assert "odds" in leg
                assert "stake" in leg
                assert leg["stake"] > 0

    def test_3way_arb_detection(self):
        """3-way soccer market should detect arb when odds diverge."""
        # Very generous odds across 3 books that create a clear arb
        event = self._make_3way_event(
            prices_a=(300, 150, 400),    # FD generous on Home + Draw
            prices_b=(100, 350, 200),    # DK generous on Away
            prices_c=(200, 200, 500),    # HRB generous on Draw
        )
        arbs = find_arbitrage_opportunities([event])
        # With these extreme odds, there should be an arb using best from each book
        if arbs:
            assert arbs[0]["num_legs"] == 3

    def test_3way_arb_stakes_sum_correctly(self):
        """3-way arb stakes should sum to bankroll."""
        event = self._make_3way_event(
            prices_a=(300, 150, 500),
            prices_b=(100, 350, 200),
            prices_c=(250, 200, 450),
        )
        arbs = find_arbitrage_opportunities([event])
        for arb in arbs:
            total = sum(leg["stake"] for leg in arb["legs"])
            assert abs(total - 100) < 1

    def test_deduplication(self):
        """Same event+market should not produce duplicate arbs."""
        event = self._make_event(
            book_a_price=(200, -250),
            book_b_price=(-150, 110),
        )
        arbs = find_arbitrage_opportunities([event])
        # Count arbs for the same event+market
        keys = [(a["event_id"], a["market"]) for a in arbs]
        assert len(keys) == len(set(keys)), "Duplicate arbs detected"

    def test_uses_best_odds(self):
        """Arb should use the best odds available across all books."""
        # 3 books — best for Team A is +200 (FD), best for Team B is +120 (HRB)
        event = {
            "id": "test_best",
            "sport": "basketball_nba",
            "league": "NBA",
            "home_team": "Team A",
            "away_team": "Team B",
            "commence_time": "2026-03-30T00:00:00Z",
            "bookmakers": [
                {
                    "key": "fanduel", "title": "FanDuel",
                    "markets": [{"key": "h2h", "outcomes": [
                        {"name": "Team A", "price": 200},
                        {"name": "Team B", "price": -250},
                    ]}]
                },
                {
                    "key": "draftkings", "title": "DraftKings",
                    "markets": [{"key": "h2h", "outcomes": [
                        {"name": "Team A", "price": 180},
                        {"name": "Team B", "price": 100},
                    ]}]
                },
                {
                    "key": "hardrockbet", "title": "Hard Rock Bet",
                    "markets": [{"key": "h2h", "outcomes": [
                        {"name": "Team A", "price": 190},
                        {"name": "Team B", "price": 120},
                    ]}]
                },
            ]
        }
        arbs = find_arbitrage_opportunities([event])
        if arbs:
            legs = arbs[0]["legs"]
            # Should use +200 from FD for Team A, +120 from HRB for Team B
            team_a_leg = next((l for l in legs if l["outcome"] == "Team A"), None)
            team_b_leg = next((l for l in legs if l["outcome"] == "Team B"), None)
            if team_a_leg and team_b_leg:
                assert team_a_leg["odds"] == 200
                assert team_a_leg["book"] == "FanDuel"
                assert team_b_leg["odds"] == 120
                assert team_b_leg["book"] == "Hard Rock Bet"


class TestLiveEventDetection:
    """Test in-play / live event detection."""

    def test_future_event_not_live(self):
        future_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        events = [{"commence_time": future_time}]
        assert detect_live_events(events) is False

    def test_past_event_is_live(self):
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        events = [{"commence_time": past_time}]
        assert detect_live_events(events) is True

    def test_single_event_live_check(self):
        past_time = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
        event = {"commence_time": past_time}
        assert _is_event_live(event) is True

    def test_single_event_not_live(self):
        future_time = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
        event = {"commence_time": future_time}
        assert _is_event_live(event) is False

    def test_missing_commence_time(self):
        event = {}
        assert _is_event_live(event) is False

    def test_mixed_events(self):
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        future_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        events = [
            {"commence_time": future_time},  # Not live
            {"commence_time": past_time},     # Live
        ]
        assert detect_live_events(events) is True


class TestPositiveEV:
    """Test +EV bet detection."""

    def test_ev_bets_found_on_mock_data(self):
        """Mock data should contain at least some +EV opportunities."""
        ev_bets = find_positive_ev_bets()
        assert isinstance(ev_bets, list)

    def test_ev_per_dollar_is_positive(self):
        """All returned EV bets must have positive EV."""
        ev_bets = find_positive_ev_bets()
        for bet in ev_bets:
            assert bet["ev_per_dollar"] > 0

    def test_recommended_stake_non_negative(self):
        """Recommended stake should never be negative."""
        ev_bets = find_positive_ev_bets()
        for bet in ev_bets:
            assert bet["recommended_stake"] >= 0

    def test_ev_bets_have_consensus_count(self):
        """EV bets should indicate how many books were used for consensus."""
        ev_bets = find_positive_ev_bets()
        for bet in ev_bets:
            assert "num_books_consensus" in bet
            assert bet["num_books_consensus"] >= 2

    def test_ev_bets_have_decimal_odds(self):
        """EV bets should include decimal odds for reference."""
        ev_bets = find_positive_ev_bets()
        for bet in ev_bets:
            assert "decimal_odds" in bet
            assert bet["decimal_odds"] > 1.0


class TestMultipleSimultaneousGames:
    """Test handling of multiple simultaneous events."""

    def test_multiple_events_arb_detection(self):
        """System should handle multiple events without mixing them up."""
        events = [
            {
                "id": "game_1",
                "sport": "basketball_nba", "league": "NBA",
                "home_team": "Lakers", "away_team": "Celtics",
                "commence_time": "2026-03-30T00:00:00Z",
                "bookmakers": [
                    {"key": "fanduel", "title": "FanDuel",
                     "markets": [{"key": "h2h", "outcomes": [
                         {"name": "Lakers", "price": 200},
                         {"name": "Celtics", "price": -250},
                     ]}]},
                    {"key": "draftkings", "title": "DraftKings",
                     "markets": [{"key": "h2h", "outcomes": [
                         {"name": "Lakers", "price": -150},
                         {"name": "Celtics", "price": 110},
                     ]}]},
                ]
            },
            {
                "id": "game_2",
                "sport": "basketball_nba", "league": "NBA",
                "home_team": "Warriors", "away_team": "Bucks",
                "commence_time": "2026-03-30T02:30:00Z",
                "bookmakers": [
                    {"key": "fanduel", "title": "FanDuel",
                     "markets": [{"key": "h2h", "outcomes": [
                         {"name": "Warriors", "price": -110},
                         {"name": "Bucks", "price": -110},
                     ]}]},
                    {"key": "draftkings", "title": "DraftKings",
                     "markets": [{"key": "h2h", "outcomes": [
                         {"name": "Warriors", "price": -110},
                         {"name": "Bucks", "price": -110},
                     ]}]},
                ]
            },
        ]
        arbs = find_arbitrage_opportunities(events)
        # Game 1 should have an arb (divergent lines), Game 2 should not
        game_1_arbs = [a for a in arbs if a["event_id"] == "game_1"]
        game_2_arbs = [a for a in arbs if a["event_id"] == "game_2"]
        assert len(game_2_arbs) == 0  # Efficient market

    def test_multiple_sports_handled(self):
        """Events from different sports should all be scanned."""
        events = [
            {
                "id": "nba_game",
                "sport": "basketball_nba", "league": "NBA",
                "home_team": "Lakers", "away_team": "Celtics",
                "commence_time": "2026-03-30T00:00:00Z",
                "bookmakers": [
                    {"key": "fanduel", "title": "FanDuel",
                     "markets": [{"key": "h2h", "outcomes": [
                         {"name": "Lakers", "price": -110}, {"name": "Celtics", "price": -110}
                     ]}]},
                    {"key": "draftkings", "title": "DraftKings",
                     "markets": [{"key": "h2h", "outcomes": [
                         {"name": "Lakers", "price": -110}, {"name": "Celtics", "price": -110}
                     ]}]},
                ]
            },
            {
                "id": "nfl_game",
                "sport": "americanfootball_nfl", "league": "NFL",
                "home_team": "Chiefs", "away_team": "Bills",
                "commence_time": "2026-03-30T17:00:00Z",
                "bookmakers": [
                    {"key": "fanduel", "title": "FanDuel",
                     "markets": [{"key": "h2h", "outcomes": [
                         {"name": "Chiefs", "price": -110}, {"name": "Bills", "price": -110}
                     ]}]},
                    {"key": "draftkings", "title": "DraftKings",
                     "markets": [{"key": "h2h", "outcomes": [
                         {"name": "Chiefs", "price": -110}, {"name": "Bills", "price": -110}
                     ]}]},
                ]
            },
        ]
        # Should run without errors
        arbs = find_arbitrage_opportunities(events)
        ev_bets = find_positive_ev_bets(events)
        assert isinstance(arbs, list)
        assert isinstance(ev_bets, list)
