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
    odds: list[OddsLine]


class ArbitrageOpportunity(BaseModel):
    event: str
    sport: str
    market: str
    book_a: str
    outcome_a: str
    odds_a: float
    book_b: str
    outcome_b: str
    odds_b: float
    arb_pct: float = Field(description="Arbitrage percentage — guaranteed profit margin")
    stake_a: float = Field(description="Optimal stake on side A for $100 total")
    stake_b: float = Field(description="Optimal stake on side B for $100 total")
    guaranteed_profit: float


class PositiveEVBet(BaseModel):
    event: str
    sport: str
    bookmaker: str
    market: str
    outcome: str
    odds: float  # American
    implied_prob: float
    true_prob: float  # From sharpest line
    edge_pct: float
    ev_per_dollar: float
    recommended_stake: float


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
