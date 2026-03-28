"""
QuadraWealth Yields Router
API endpoints for savings & yield recommendations.
"""
from fastapi import APIRouter, Query
from typing import Optional

from backend.services.yield_service import get_current_yields, recommend_allocation

router = APIRouter()


@router.get("/current")
async def current_yields():
    """Get current yield rates for all vehicles and macro indicators."""
    return get_current_yields()


@router.post("/recommend")
async def yield_recommendation(
    inflation_rate: Optional[float] = None,
    fed_funds_rate: Optional[float] = None,
    gdp_growth: Optional[float] = None,
    risk_tolerance: str = "moderate",
):
    """
    Get recommended yield allocation based on macro conditions.
    Pass custom macro values to simulate different scenarios.
    """
    return recommend_allocation(
        inflation_rate=inflation_rate,
        fed_funds_rate=fed_funds_rate,
        gdp_growth=gdp_growth,
        risk_tolerance=risk_tolerance,
    )
