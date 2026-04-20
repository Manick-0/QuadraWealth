"""
QuadraWealth Pydantic Schemas
Request/response models for all API endpoints.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── User Profile ──────────────────────────────────────────

class UserProfileCreate(BaseModel):
    username: str = "default_user"
    risk_tolerance: str = Field(default="moderate", pattern="^(conservative|moderate|aggressive)$")
    investment_goals: list[str] = ["growth"]
    preferred_sectors: list[str] = ["tech"]
    capital_available: float = 10000.0


class UserProfileResponse(UserProfileCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Stocks (Mode 1) ──────────────────────────────────────

class StockQuote(BaseModel):
    ticker: str
    name: str
    price: float
    change: float
    change_pct: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    sector: Optional[str] = None
    week52_high: Optional[float] = None
    week52_low: Optional[float] = None


class StockRecommendation(BaseModel):
    ticker: str
    name: str
    price: float
    score: float = Field(description="0-100 recommendation score")
    reasoning: str
    risk_level: str  # low, medium, high
    sector: str
    signals: list[str]  # ["momentum_bullish", "sector_match", "value_play"]


class PortfolioPositionSchema(BaseModel):
    id: Optional[int] = None
    ticker: str
    shares: float
    avg_cost: float
    current_price: Optional[float] = None
    total_value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None


class PortfolioAction(BaseModel):
    ticker: str
    action: str = Field(pattern="^(buy|sell)$")
    shares: float


class MarketOverview(BaseModel):
    indices: list[StockQuote]
    top_gainers: list[StockQuote]
    top_losers: list[StockQuote]
    recommendations: list[StockRecommendation]


# ─── Betting / The Edge (Mode 2) ──────────────────────────

class OddsLine(BaseModel):
    bookmaker: str
    bookmaker_key: str = ""
    market: str  # h2h, spreads, totals
    outcome: str  # team name or Over/Under
    price: float  # American odds (-110, +150, etc.)
    point: Optional[float] = None  # spread or total line


class BettingEvent(BaseModel):
    id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    commence_time: str
    is_live: bool = False
    odds: list[OddsLine]


class ArbLeg(BaseModel):
    """A single leg of an N-way arbitrage opportunity."""
    book: str
    book_key: str = ""
    outcome: str
    odds: float  # American
    decimal_odds: float
    implied_prob: float
    stake: float


class ArbitrageOpportunity(BaseModel):
    event: str
    event_id: str = ""
    sport: str
    market: str
    point: Optional[float] = None
    commence_time: str = ""
    is_live: bool = False
    legs: list[ArbLeg] = []
    num_legs: int = 2
    arb_pct: float = Field(description="Arbitrage percentage — guaranteed profit margin")
    arb_sum: float = Field(default=0, description="Sum of implied probabilities (< 1.0 = arb)")
    guaranteed_profit: float
    # Legacy compat for 2-way display
    book_a: str = ""
    outcome_a: str = ""
    odds_a: float = 0
    stake_a: float = Field(default=0, description="Optimal stake on side A for $100 total")
    book_b: str = ""
    outcome_b: str = ""
    odds_b: float = 0
    stake_b: float = Field(default=0, description="Optimal stake on side B for $100 total")


class PositiveEVBet(BaseModel):
    event: str
    sport: str
    bookmaker: str
    bookmaker_key: str = ""
    market: str
    outcome: str
    point: Optional[float] = None
    odds: float  # American
    decimal_odds: float = 0
    implied_prob: float
    true_prob: float  # From consensus across books
    edge_pct: float
    ev_per_dollar: float
    recommended_stake: float
    num_books_consensus: int = 0
    commence_time: str = ""
    is_live: bool = False


class PollerStatus(BaseModel):
    """Health and metrics for the background odds poller."""
    is_running: bool = False
    data_source: str = "unknown"
    is_live: bool = False
    last_poll: Optional[str] = None
    poll_count: int = 0
    error_count: int = 0
    event_count: int = 0
    arb_count: int = 0
    ev_bet_count: int = 0
    has_live_events: bool = False
    api_requests_remaining: Optional[int] = None
    poll_duration_ms: float = 0
    poll_interval: int = 30


# ─── Savings & Yields (Mode 3) ────────────────────────────

class YieldVehicle(BaseModel):
    name: str
    category: str  # hysa, tbill, bond, gold, commodity
    current_yield: float
    risk_level: str  # very_low, low, medium
    liquidity: str  # instant, days, weeks
    min_investment: float
    description: str


class MacroIndicators(BaseModel):
    inflation_rate: float
    fed_funds_rate: float
    gdp_growth: float
    unemployment: float
    sp500_pe: float
    vix: float
    ten_year_yield: float


class YieldRecommendation(BaseModel):
    macro: MacroIndicators
    vehicles: list[YieldVehicle]
    allocations: dict[str, float]  # {"hysa": 30, "tbill": 20, "gold": 50}
    rationale: str


# ─── Real Estate (Mode 4) ─────────────────────────────────

class Property(BaseModel):
    id: int
    address: str
    city: str
    state: str
    zip_code: str
    property_type: str  # SFH, Condo, Multi-family, Townhouse
    price: float
    bedrooms: int
    bathrooms: float
    sqft: int
    year_built: int
    expected_rent: float
    property_tax: float
    insurance: float
    maintenance_cost: float
    hoa_fee: float = 0
    market_growth_rate: float  # Annual appreciation %
    lat: Optional[float] = None
    lng: Optional[float] = None


class PropertyAnalysis(BaseModel):
    property: Property
    noi: float = Field(description="Net Operating Income (annual)")
    cap_rate: float = Field(description="Cap Rate %")
    cash_on_cash: float = Field(description="Cash-on-Cash Return % (assuming 20% down)")
    monthly_cash_flow: float
    annual_cash_flow: float
    total_monthly_expenses: float
    down_payment: float
    mortgage_payment: float
    goal_score: float = Field(description="0-100 score based on selected investment goal")
    goal: str


# ─── Multi-Agent AI (New) ─────────────────────────────────

class AgentChatRequest(BaseModel):
    query: str
    risk_tolerance: str = "moderate"


class ReasoningStep(BaseModel):
    step: str


class AgentDetail(BaseModel):
    agent: str
    role: str
    response: str
    reasoning_steps: list[str] = []


class AgentChatResponse(BaseModel):
    query: str
    response: str
    agents_involved: list[str]
    agent_details: list[AgentDetail]
    execution_plan: dict
