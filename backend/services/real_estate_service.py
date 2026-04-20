from __future__ import annotations
"""
QuadraWealth Real Estate Service
Property screener with Cap Rate and Cash-on-Cash return calculations.

Live data source: Realty Mole Property API via RapidAPI.
Fallback: 50-property mock dataset.
"""
import json
import logging
import requests as _req
from pathlib import Path
from typing import Optional

from backend.config import settings

logger = logging.getLogger("realestate.service")

# ─────────────────────── US States lookup ───────────────────────
US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia",
}

# ─────────────────────── Mock Data ───────────────────────
def load_properties() -> list[dict]:
    """Load mock property dataset."""
    data_path = Path(__file__).parent.parent / "data" / "mock_properties.json"
    with open(data_path, "r") as f:
        return json.load(f)


# ─────────────────────── Live API ───────────────────────
_REALTY_MOLE_BASE = "https://realty-mole-property-api.p.rapidapi.com"
_api_failed = False  # Set True on auth failure to avoid repeated 401s


def _normalize_live_property(raw: dict, idx: int) -> dict:
    """
    Convert a Realty Mole API response dict into our standard property schema.
    Fields vary by property – fill gaps with sensible defaults.
    """
    price = raw.get("price") or raw.get("lastSalePrice") or raw.get("assessedValue") or 250000
    rent = raw.get("rentEstimate") or raw.get("rent") or int(price * 0.007)  # ~0.7% of price
    sqft = raw.get("squareFootage") or raw.get("lotSize") or 1400
    beds = raw.get("bedrooms") or 3
    baths = raw.get("bathrooms") or 2
    year = raw.get("yearBuilt") or 2010

    # Taxes / insurance estimation
    county = raw.get("county", "")
    tax_rate = 0.012  # default 1.2%
    prop_tax = raw.get("propertyTaxes") or int(price * tax_rate)
    insurance = int(price * 0.004)  # ~0.4%
    maintenance = int(price * 0.01)  # ~1%
    hoa = 0  # Realty Mole doesn't provide HOA

    # Property type mapping
    ptype_raw = (raw.get("propertyType") or "Single Family").lower()
    if "condo" in ptype_raw:
        ptype = "Condo"
        hoa = 300  # Assume condo HOA
    elif "town" in ptype_raw:
        ptype = "Townhouse"
        hoa = 180
    elif "multi" in ptype_raw or "duplex" in ptype_raw or "triplex" in ptype_raw:
        ptype = "Multi-family"
    else:
        ptype = "SFH"

    # Coordinates
    lat = raw.get("latitude") or raw.get("lat") or 0
    lng = raw.get("longitude") or raw.get("lng") or raw.get("lon") or 0

    city = raw.get("city", "Unknown")
    state = raw.get("state", "")
    address_line = raw.get("addressLine1") or raw.get("formattedAddress") or raw.get("address", "")

    return {
        "id": 1000 + idx,
        "address": address_line,
        "city": city,
        "state": state,
        "zip_code": raw.get("zipCode") or raw.get("zip", ""),
        "property_type": ptype,
        "price": price,
        "bedrooms": beds,
        "bathrooms": baths,
        "sqft": sqft,
        "year_built": year,
        "expected_rent": rent,
        "property_tax": prop_tax,
        "insurance": insurance,
        "maintenance_cost": maintenance,
        "hoa_fee": hoa,
        "market_growth_rate": round(3.0 + (hash(city) % 30) / 10, 1),  # Deterministic per city
        "lat": lat,
        "lng": lng,
        "_source": "live",
    }


def fetch_live_properties(
    city: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = 20,
) -> list[dict]:
    """
    Fetch properties from Realty Mole Property API on RapidAPI.
    Tries multiple endpoints: /randomProperties (free tier), /saleListings (paid).
    Returns normalized property list or empty list on failure.
    """
    global _api_failed

    api_key = settings.RAPIDAPI_KEY
    if not api_key or _api_failed:
        return []

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "realty-mole-property-api.p.rapidapi.com",
    }

    # Endpoints to try in order (free-tier first, then paid)
    endpoints = [
        ("/randomProperties", {"limit": str(min(limit, 50))}),
        ("/saleListings", {
            "limit": str(min(limit, 50)),
            **({"city": city} if city else {}),
            **({"state": state} if state else {}),
            **({"city": "Austin", "state": "TX"} if (not city and not state) else {}),
        }),
        ("/rentalListings", {
            "limit": str(min(limit, 50)),
            **({"city": city} if city else {}),
            **({"state": state} if state else {}),
            **({"city": "Austin", "state": "TX"} if (not city and not state) else {}),
        }),
    ]

    for endpoint_path, params in endpoints:
        try:
            resp = _req.get(
                f"{_REALTY_MOLE_BASE}{endpoint_path}",
                headers=headers,
                params=params,
                timeout=15,
            )

            if resp.status_code == 401 or resp.status_code == 403:
                logger.error("🔑 RapidAPI auth failed — falling back to mock data")
                _api_failed = True
                return []

            if resp.status_code == 429:
                logger.warning("⏳ RapidAPI rate limit hit on %s — using mock data", endpoint_path)
                return []

            if resp.status_code == 404:
                logger.debug("Endpoint %s not available, trying next...", endpoint_path)
                continue

            if resp.status_code != 200:
                logger.warning("Realty Mole %s returned %d: %s", endpoint_path, resp.status_code, resp.text[:200])
                continue

            data = resp.json()
            if not isinstance(data, list):
                data = [data]

            result = [_normalize_live_property(p, i) for i, p in enumerate(data) if p]
            logger.info("📍 Fetched %d live properties from Realty Mole %s", len(result), endpoint_path)
            return result

        except _req.exceptions.Timeout:
            logger.warning("Realty Mole %s timed out", endpoint_path)
            continue
        except Exception as e:
            logger.error("Realty Mole %s error: %s", endpoint_path, e)
            continue

    logger.warning("All Realty Mole endpoints failed — falling back to mock data")
    return []


def reset_api_state():
    """Reset the API failure flag (called on service restart)."""
    global _api_failed
    _api_failed = False


# ─────────────────────── Calculations ───────────────────────
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

        if prop["year_built"] >= 2018:
            score += 10
        elif prop["year_built"] >= 2012:
            score += 5

    elif goal == "long_term":
        if cap_rate > 8:
            score += 20
        elif cap_rate > 6:
            score += 12
        elif cap_rate > 4:
            score += 5

        if 3.0 <= growth_rate <= 5.0:
            score += 15
        elif growth_rate > 5.0:
            score += 8

        if prop["property_type"] in ["SFH", "Multi-family"]:
            score += 10

        expense_ratio = total_monthly_expenses / monthly_rent if monthly_rent > 0 else 2
        if expense_ratio < 0.7:
            score += 10
        elif expense_ratio < 0.85:
            score += 5

    elif goal == "cash_flow":
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

        if prop["property_type"] == "Multi-family":
            score += 10

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


# ─────────────────────── Query helpers ───────────────────────
def get_all_properties(
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_bedrooms: Optional[int] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
) -> list[dict]:
    """Return filtered list of properties. Tries live API first, falls back to mock."""
    # Try live API
    if settings.USE_LIVE_REALESTATE and settings.RAPIDAPI_KEY:
        live = fetch_live_properties(city=city, state=state, limit=50)
        if live:
            properties = live
        else:
            properties = load_properties()
    else:
        properties = load_properties()

    # Apply filters
    if property_type:
        properties = [p for p in properties if p["property_type"].lower() == property_type.lower()]
    if min_price is not None:
        properties = [p for p in properties if p["price"] >= min_price]
    if max_price is not None:
        properties = [p for p in properties if p["price"] <= max_price]
    if min_bedrooms is not None:
        properties = [p for p in properties if p["bedrooms"] >= min_bedrooms]
    # Only filter by state/city on mock data (live already has location filter)
    if state and not any(p.get("_source") == "live" for p in properties):
        properties = [p for p in properties if p["state"].upper() == state.upper()]
    if city and not any(p.get("_source") == "live" for p in properties):
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


def get_available_locations() -> dict:
    """
    Return available cities and states from mock data for the location filter UI.
    """
    properties = load_properties()
    states = sorted(set(p["state"] for p in properties))
    cities_by_state = {}
    for p in properties:
        st = p["state"]
        if st not in cities_by_state:
            cities_by_state[st] = set()
        cities_by_state[st].add(p["city"])

    cities_by_state = {k: sorted(v) for k, v in cities_by_state.items()}

    return {
        "states": states,
        "cities_by_state": cities_by_state,
        "all_cities": sorted(set(p["city"] for p in properties)),
    }
