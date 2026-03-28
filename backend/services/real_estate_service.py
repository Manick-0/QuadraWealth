"""
QuadraWealth Real Estate Service
Property screener with Cap Rate and Cash-on-Cash return calculations.
"""
import json
from pathlib import Path
from typing import Optional


def load_properties() -> list[dict]:
    """Load mock property dataset."""
    data_path = Path(__file__).parent.parent / "data" / "mock_properties.json"
    with open(data_path, "r") as f:
        return json.load(f)


def calculate_property_analysis(
    prop: dict,
    goal: str = "cash_flow",
    down_payment_pct: float = 20.0,
    mortgage_rate: float = 6.5,
    mortgage_years: int = 30,
) -> dict:
    """
    Full financial analysis for a single property.

    Calculations:
    - NOI = (Monthly Rent × 12) - Property Tax - Insurance - Maintenance - HOA
    - Cap Rate = (NOI / Purchase Price) × 100
    - Mortgage = standard amortization formula
    - Cash-on-Cash = (Annual Cash Flow / Total Cash Invested) × 100

    Goal scoring:
    - "appreciation": weight market_growth_rate + low price/sqft
    - "long_term": weight cap_rate + market stability
    - "cash_flow": weight cash-on-cash return + monthly cash flow
    """
    price = prop["price"]
    monthly_rent = prop["expected_rent"]
    annual_rent = monthly_rent * 12
    property_tax = prop["property_tax"]
    insurance = prop["insurance"]
    maintenance = prop["maintenance_cost"]
    hoa = prop.get("hoa_fee", 0) * 12  # Convert monthly to annual
    growth_rate = prop.get("market_growth_rate", 3.0)

    # ── NOI Calculation ──
    annual_expenses = property_tax + insurance + maintenance + hoa
    noi = annual_rent - annual_expenses

    # ── Cap Rate ──
    cap_rate = (noi / price) * 100 if price > 0 else 0

    # ── Mortgage Calculation ──
    down_payment = price * (down_payment_pct / 100)
    loan_amount = price - down_payment
    monthly_rate = (mortgage_rate / 100) / 12
    n_payments = mortgage_years * 12

    if monthly_rate > 0:
        mortgage_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** n_payments
        ) / ((1 + monthly_rate) ** n_payments - 1)
    else:
        mortgage_payment = loan_amount / n_payments

    annual_mortgage = mortgage_payment * 12

    # ── Cash Flow ──
    annual_cash_flow = noi - annual_mortgage
    monthly_cash_flow = annual_cash_flow / 12

    # ── Cash-on-Cash Return ──
    # Total cash invested = down payment + estimated closing costs (3%)
    closing_costs = price * 0.03
    total_cash_invested = down_payment + closing_costs
    cash_on_cash = (annual_cash_flow / total_cash_invested) * 100 if total_cash_invested > 0 else 0

    # ── Monthly expense breakdown ──
    total_monthly_expenses = (annual_expenses / 12) + mortgage_payment

    # ── Goal-based scoring (0-100) ──
    score = 50  # Base

    if goal == "appreciation":
        # Weight market growth and price/sqft ratio
        if growth_rate > 5.0:
            score += 25
        elif growth_rate > 4.0:
            score += 15
        elif growth_rate > 3.0:
            score += 8

        price_per_sqft = price / prop["sqft"] if prop["sqft"] > 0 else 999
        if price_per_sqft < 150:
            score += 15
        elif price_per_sqft < 200:
            score += 10
        elif price_per_sqft < 250:
            score += 5

        # Newer properties appreciate better
        if prop["year_built"] >= 2018:
            score += 10
        elif prop["year_built"] >= 2012:
            score += 5

    elif goal == "long_term":
        # Weight cap rate + market stability
        if cap_rate > 8:
            score += 20
        elif cap_rate > 6:
            score += 12
        elif cap_rate > 4:
            score += 5

        if 3.0 <= growth_rate <= 5.0:
            score += 15  # Stable, moderate growth
        elif growth_rate > 5.0:
            score += 8

        # Multi-family and SFH are better long-term holds
        if prop["property_type"] in ["SFH", "Multi-family"]:
            score += 10

        # Lower monthly expenses relative to rent
        expense_ratio = total_monthly_expenses / monthly_rent if monthly_rent > 0 else 2
        if expense_ratio < 0.7:
            score += 10
        elif expense_ratio < 0.85:
            score += 5

    elif goal == "cash_flow":
        # Weight cash-on-cash return and monthly cash flow
        if cash_on_cash > 10:
            score += 25
        elif cash_on_cash > 6:
            score += 15
        elif cash_on_cash > 3:
            score += 8

        if monthly_cash_flow > 500:
            score += 15
        elif monthly_cash_flow > 200:
            score += 10
        elif monthly_cash_flow > 0:
            score += 5

        # Multi-family is great for cash flow
        if prop["property_type"] == "Multi-family":
            score += 10

        # Low property tax helps cash flow
        tax_rate = (property_tax / price * 100) if price > 0 else 999
        if tax_rate < 1.0:
            score += 8
        elif tax_rate < 1.5:
            score += 4

    score = max(0, min(100, score))

    return {
        "property": prop,
        "noi": round(noi, 2),
        "cap_rate": round(cap_rate, 2),
        "cash_on_cash": round(cash_on_cash, 2),
        "monthly_cash_flow": round(monthly_cash_flow, 2),
        "annual_cash_flow": round(annual_cash_flow, 2),
        "total_monthly_expenses": round(total_monthly_expenses, 2),
        "down_payment": round(down_payment, 2),
        "mortgage_payment": round(mortgage_payment, 2),
        "goal_score": score,
        "goal": goal,
    }


def get_all_properties(
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_bedrooms: Optional[int] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
) -> list[dict]:
    """Return filtered list of properties."""
    properties = load_properties()

    if property_type:
        properties = [p for p in properties if p["property_type"].lower() == property_type.lower()]
    if min_price is not None:
        properties = [p for p in properties if p["price"] >= min_price]
    if max_price is not None:
        properties = [p for p in properties if p["price"] <= max_price]
    if min_bedrooms is not None:
        properties = [p for p in properties if p["bedrooms"] >= min_bedrooms]
    if state:
        properties = [p for p in properties if p["state"].upper() == state.upper()]
    if city:
        city_lower = city.lower()
        properties = [p for p in properties if city_lower in p.get("city", "").lower()]

    return properties


def get_hottest_properties(
    goal: str = "cash_flow",
    limit: int = 10,
    **filter_kwargs,
) -> list[dict]:
    """Return top properties ranked by goal score."""
    properties = get_all_properties(**filter_kwargs)

    analyzed = []
    for prop in properties:
        analysis = calculate_property_analysis(prop, goal=goal)
        analyzed.append(analysis)

    # Sort by goal score descending
    analyzed.sort(key=lambda x: x["goal_score"], reverse=True)
    return analyzed[:limit]


def analyze_property_by_id(property_id: int, goal: str = "cash_flow") -> Optional[dict]:
    """Analyze a specific property by its ID."""
    properties = load_properties()
    prop = next((p for p in properties if p["id"] == property_id), None)

    if prop is None:
        return None

    return calculate_property_analysis(prop, goal=goal)
