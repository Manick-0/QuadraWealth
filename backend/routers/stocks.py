from __future__ import annotations
"""
QuadraWealth Stocks Router
API endpoints for stock portfolio management and recommendations.
"""
from fastapi import APIRouter, Query
from typing import Optional

from backend.services.stock_service import (
    get_market_overview,
    get_recommendations,
    analyze_stock,
    get_stock_quote,
)

router = APIRouter()


@router.get("/market-overview")
async def market_overview():
    """Get market indices, top gainers, and top losers."""
    return get_market_overview()


@router.post("/recommendations")
async def stock_recommendations(
    risk_tolerance: str = "moderate",
    preferred_sectors: list[str] = ["tech", "finance"],
    capital: float = 10000.0,
):
    """Get RAG-powered stock recommendations based on user profile."""
    return get_recommendations(
        risk_tolerance=risk_tolerance,
        preferred_sectors=preferred_sectors,
        capital=capital,
    )


@router.get("/analyze/{ticker}")
async def analyze_ticker(ticker: str):
    """Deep-dive analysis of a specific stock ticker."""
    return analyze_stock(ticker.upper())


@router.get("/quote/{ticker}")
async def get_quote(ticker: str):
    """Get a real-time quote for a specific ticker."""
    quote = get_stock_quote(ticker.upper())
    if quote:
        return quote.model_dump()
    return {"error": f"Could not fetch data for {ticker}"}
