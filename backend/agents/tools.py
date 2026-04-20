from __future__ import annotations
"""
QuadraWealth Agent Tools
Wraps existing backend services as callable tools for AI agents.
Each tool has:
  - A name and description (for LLM function calling)
  - An OpenAI-compatible JSON schema
  - An execute() function that invokes the real service
"""
import json
import logging
from typing import Any

logger = logging.getLogger("agents.tools")


# ═══════════════════════════════════════════════════════════════
#  TOOL REGISTRY
# ═══════════════════════════════════════════════════════════════

class Tool:
    """Represents a callable tool that an agent can invoke."""

    def __init__(self, name: str, description: str, parameters: dict, func):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def to_openai_schema(self) -> dict:
        """Convert to OpenAI function calling format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, **kwargs) -> str:
        """Execute the tool and return a JSON string result."""
        try:
            result = self.func(**kwargs)
            if isinstance(result, str):
                return result
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error("Tool '%s' error: %s", self.name, e)
            return json.dumps({"error": str(e)})


# ═══════════════════════════════════════════════════════════════
#  TOOL IMPLEMENTATIONS — wrapping existing services
# ═══════════════════════════════════════════════════════════════

def _get_stock_quote(ticker: str) -> dict:
    from backend.services.stock_service import get_stock_quote
    quote = get_stock_quote(ticker)
    if quote:
        return quote.model_dump()
    return {"error": f"No data for {ticker}"}


def _get_stock_recommendations(
    risk_tolerance: str = "moderate",
    sectors: list[str] | None = None,
) -> dict:
    from backend.services.stock_service import get_recommendations
    recs = get_recommendations(
        risk_tolerance=risk_tolerance,
        preferred_sectors=sectors or ["tech", "finance"],
    )
    return {"recommendations": recs[:8], "total": len(recs)}


def _analyze_stock(ticker: str) -> dict:
    from backend.services.stock_service import analyze_stock
    return analyze_stock(ticker)


def _get_market_overview() -> dict:
    from backend.services.stock_service import get_market_overview
    return get_market_overview()


def _search_financial_news(query: str, sector: str | None = None, n_results: int = 5) -> dict:
    from backend.services.rag_engine import query_relevant_news
    results = query_relevant_news(query, n_results=n_results, sector_filter=sector)
    return {"query": query, "results": results, "count": len(results)}


def _find_arbitrage() -> dict:
    from backend.services.betting_service import find_arbitrage_opportunities, fetch_live_odds
    events = fetch_live_odds()
    arbs = find_arbitrage_opportunities(events)
    return {
        "arbitrage_opportunities": arbs[:10],
        "total": len(arbs),
        "total_events_scanned": len(events),
    }


def _find_positive_ev() -> dict:
    from backend.services.betting_service import find_positive_ev_bets, fetch_live_odds
    events = fetch_live_odds()
    ev_bets = find_positive_ev_bets(events)
    return {
        "positive_ev_bets": ev_bets[:10],
        "total": len(ev_bets),
        "total_events_scanned": len(events),
    }


def _get_odds(sport: str | None = None) -> dict:
    from backend.services.betting_service import get_odds_by_sport, fetch_live_odds
    if sport:
        events = get_odds_by_sport(sport)
    else:
        events = fetch_live_odds()
    return {"events": events[:10], "total": len(events)}


def _get_yield_recommendation(risk_tolerance: str = "moderate") -> dict:
    from backend.services.yield_service import recommend_allocation
    return recommend_allocation(risk_tolerance=risk_tolerance)


def _get_macro_indicators() -> dict:
    from backend.services.yield_service import get_current_yields
    data = get_current_yields()
    return data.get("macro", {})


def _search_properties(
    goal: str = "cash_flow",
    limit: int = 5,
    property_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    state: str | None = None,
) -> dict:
    from backend.services.real_estate_service import get_hottest_properties
    kwargs = {}
    if property_type:
        kwargs["property_type"] = property_type
    if min_price:
        kwargs["min_price"] = min_price
    if max_price:
        kwargs["max_price"] = max_price
    if state:
        kwargs["state"] = state

    props = get_hottest_properties(goal=goal, limit=limit, **kwargs)
    return {"properties": props[:limit], "goal": goal, "total": len(props)}


def _analyze_property(property_id: int, goal: str = "cash_flow") -> dict:
    from backend.services.real_estate_service import analyze_property_by_id
    result = analyze_property_by_id(property_id, goal=goal)
    if result:
        return result
    return {"error": f"Property {property_id} not found"}


def _get_portfolio_assessment(risk_tolerance: str = "moderate") -> dict:
    """Cross-mode portfolio assessment combining data from all modes."""
    from backend.services.stock_service import get_market_overview
    from backend.services.yield_service import recommend_allocation
    from backend.services.betting_service import find_arbitrage_opportunities, fetch_live_odds

    market = get_market_overview()
    yields = recommend_allocation(risk_tolerance=risk_tolerance)
    events = fetch_live_odds()
    arbs = find_arbitrage_opportunities(events)

    return {
        "market_overview": {
            "indices": market.get("indices", [])[:3],
            "top_gainers": [g["ticker"] for g in market.get("top_gainers", [])[:3]],
            "top_losers": [l["ticker"] for l in market.get("top_losers", [])[:3]],
        },
        "yield_allocation": yields.get("allocations", {}),
        "yield_rationale": yields.get("rationale", ""),
        "betting_opportunities": {
            "arbitrage_count": len(arbs),
            "top_arb": arbs[0] if arbs else None,
        },
        "risk_tolerance": risk_tolerance,
    }


# ═══════════════════════════════════════════════════════════════
#  TOOL DEFINITIONS (OpenAI function schema format)
# ═══════════════════════════════════════════════════════════════

# ── Stock Tools ──
STOCK_TOOLS = [
    Tool(
        name="get_stock_quote",
        description="Get real-time price, P/E, volume, and market cap for a stock ticker symbol.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. AAPL, MSFT"},
            },
            "required": ["ticker"],
        },
        func=_get_stock_quote,
    ),
    Tool(
        name="get_stock_recommendations",
        description="Get AI-scored stock recommendations based on fundamental analysis (P/E, ROE, EPS, D/E, EMA200) and news sentiment. Scores stocks 0-100.",
        parameters={
            "type": "object",
            "properties": {
                "risk_tolerance": {
                    "type": "string",
                    "enum": ["conservative", "moderate", "aggressive"],
                    "description": "Investor risk tolerance level",
                },
                "sectors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Preferred sectors: tech, finance, healthcare, consumer, energy",
                },
            },
        },
        func=_get_stock_recommendations,
    ),
    Tool(
        name="analyze_stock",
        description="Deep-dive analysis of a single stock: technicals, fundamentals, 6-month history, and relevant RAG news.",
        parameters={
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker symbol"},
            },
            "required": ["ticker"],
        },
        func=_analyze_stock,
    ),
    Tool(
        name="get_market_overview",
        description="Get market indices (S&P 500, NASDAQ, Dow Jones), top gainers, and top losers from the watchlist.",
        parameters={"type": "object", "properties": {}},
        func=_get_market_overview,
    ),
]

# ── RAG / News Tool ──
NEWS_TOOLS = [
    Tool(
        name="search_financial_news",
        description="Search the financial news knowledge base using RAG (Retrieval-Augmented Generation) via ChromaDB. Returns relevant news snippets with sentiment analysis.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for financial news"},
                "sector": {"type": "string", "description": "Optional sector filter: tech, finance, healthcare, consumer, energy"},
                "n_results": {"type": "integer", "description": "Number of results to return (default 5)"},
            },
            "required": ["query"],
        },
        func=_search_financial_news,
    ),
]

# ── Betting / Edge Tools ──
EDGE_TOOLS = [
    Tool(
        name="find_arbitrage",
        description="Scan all sportsbook events for arbitrage opportunities. Detects when combined implied probability < 100% across books, guaranteeing profit.",
        parameters={"type": "object", "properties": {}},
        func=_find_arbitrage,
    ),
    Tool(
        name="find_positive_ev",
        description="Find positive Expected Value (+EV) bets by comparing each book's odds to the consensus probability across all books. Uses Kelly Criterion for sizing.",
        parameters={"type": "object", "properties": {}},
        func=_find_positive_ev,
    ),
    Tool(
        name="get_odds",
        description="Get current odds and lines from sportsbooks (FanDuel, DraftKings, Hard Rock, BetMGM, Caesars).",
        parameters={
            "type": "object",
            "properties": {
                "sport": {"type": "string", "description": "Sport key: basketball_nba, baseball_mlb"},
            },
        },
        func=_get_odds,
    ),
]

# ── Yield / Savings Tools ──
YIELD_TOOLS = [
    Tool(
        name="get_yield_recommendation",
        description="Get macro-driven yield vehicle allocation recommendation. Analyzes inflation, Fed funds rate, and GDP growth to recommend allocation across HYSA, T-Bills, bonds, gold, and commodities.",
        parameters={
            "type": "object",
            "properties": {
                "risk_tolerance": {
                    "type": "string",
                    "enum": ["conservative", "moderate", "aggressive"],
                },
            },
        },
        func=_get_yield_recommendation,
    ),
    Tool(
        name="get_macro_indicators",
        description="Get current macroeconomic indicators: Fed funds rate, inflation, GDP growth, unemployment, yield curve spread.",
        parameters={"type": "object", "properties": {}},
        func=_get_macro_indicators,
    ),
]

# ── Real Estate Tools ──
REALESTATE_TOOLS = [
    Tool(
        name="search_properties",
        description="Search and rank investment properties by goal (cash_flow, appreciation, long_term). Calculates Cap Rate, NOI, and Cash-on-Cash return.",
        parameters={
            "type": "object",
            "properties": {
                "goal": {
                    "type": "string",
                    "enum": ["cash_flow", "appreciation", "long_term"],
                    "description": "Investment goal for scoring",
                },
                "limit": {"type": "integer", "description": "Max properties to return"},
                "property_type": {"type": "string", "description": "SFH, Condo, Townhouse, Multi-family"},
                "state": {"type": "string", "description": "US state abbreviation"},
                "max_price": {"type": "number", "description": "Maximum price filter"},
            },
        },
        func=_search_properties,
    ),
    Tool(
        name="analyze_property",
        description="Full financial analysis of a property: NOI, cap rate, cash-on-cash return, mortgage calculation, goal-based score.",
        parameters={
            "type": "object",
            "properties": {
                "property_id": {"type": "integer", "description": "Property ID to analyze"},
                "goal": {"type": "string", "enum": ["cash_flow", "appreciation", "long_term"]},
            },
            "required": ["property_id"],
        },
        func=_analyze_property,
    ),
]

# ── Cross-Mode Tool ──
PORTFOLIO_TOOLS = [
    Tool(
        name="get_portfolio_assessment",
        description="Comprehensive cross-mode portfolio assessment combining market overview, yield allocation, and betting opportunities based on risk profile.",
        parameters={
            "type": "object",
            "properties": {
                "risk_tolerance": {
                    "type": "string",
                    "enum": ["conservative", "moderate", "aggressive"],
                },
            },
        },
        func=_get_portfolio_assessment,
    ),
]


# ── Get all tools ──
ALL_TOOLS = STOCK_TOOLS + NEWS_TOOLS + EDGE_TOOLS + YIELD_TOOLS + REALESTATE_TOOLS + PORTFOLIO_TOOLS


def get_tools_by_name(names: list[str]) -> list[Tool]:
    """Get specific tools by name."""
    return [t for t in ALL_TOOLS if t.name in names]


def get_tool_by_name(name: str) -> Tool | None:
    """Get a single tool by name."""
    for t in ALL_TOOLS:
        if t.name == name:
            return t
    return None


def get_all_openai_schemas() -> list[dict]:
    """Get all tool schemas in OpenAI format."""
    return [t.to_openai_schema() for t in ALL_TOOLS]
