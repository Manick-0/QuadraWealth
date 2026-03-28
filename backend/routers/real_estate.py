"""
QuadraWealth Real Estate Router
API endpoints for property screening and investment analysis.
"""
from fastapi import APIRouter, Query
from typing import Optional

from backend.services.real_estate_service import (
    get_all_properties,
    get_hottest_properties,
    analyze_property_by_id,
)

router = APIRouter()


@router.get("/properties")
async def list_properties(
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_bedrooms: Optional[int] = None,
    state: Optional[str] = None,
):
    """List properties with optional filters."""
    return get_all_properties(
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        state=state,
    )


@router.get("/analyze/{property_id}")
async def analyze_property(
    property_id: int,
    goal: str = Query(default="cash_flow", pattern="^(appreciation|long_term|cash_flow)$"),
):
    """Get full financial analysis for a specific property."""
    result = analyze_property_by_id(property_id, goal=goal)
    if result is None:
        return {"error": f"Property {property_id} not found"}
    return result


@router.get("/hottest")
async def hottest_properties(
    goal: str = Query(default="cash_flow", pattern="^(appreciation|long_term|cash_flow)$"),
    limit: int = Query(default=10, ge=1, le=50),
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    state: Optional[str] = None,
):
    """Get top-ranked properties by selected investment goal."""
    return get_hottest_properties(
        goal=goal,
        limit=limit,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        state=state,
    )
