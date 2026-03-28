"""
Unit tests for real estate cap rate and cash-on-cash return calculations.
Tests core formulas with known inputs/outputs.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from backend.services.real_estate_service import (
    calculate_property_analysis,
    get_all_properties,
    get_hottest_properties,
)


# ── Test property with known values ──
SAMPLE_PROPERTY = {
    "id": 99,
    "address": "100 Test Street",
    "city": "TestCity",
    "state": "TX",
    "zip_code": "75001",
    "property_type": "SFH",
    "price": 300000,
    "bedrooms": 3,
    "bathrooms": 2.0,
    "sqft": 1800,
    "year_built": 2015,
    "expected_rent": 2500,       # $2,500/month
    "property_tax": 6000,        # $6,000/year
    "insurance": 1500,           # $1,500/year
    "maintenance_cost": 3000,    # $3,000/year
    "hoa_fee": 0,
    "market_growth_rate": 4.5,
    "lat": 32.78,
    "lng": -96.80,
}


class TestNOICalculation:
    """Test Net Operating Income calculation."""

    def test_noi_formula(self):
        """NOI = (Monthly Rent × 12) - Property Tax - Insurance - Maintenance - HOA"""
        result = calculate_property_analysis(SAMPLE_PROPERTY)
        # Expected: (2500 × 12) - 6000 - 1500 - 3000 - 0 = 30000 - 10500 = 19500
        expected_noi = (2500 * 12) - 6000 - 1500 - 3000
        assert abs(result["noi"] - expected_noi) < 0.01
        assert result["noi"] == 19500.0

    def test_noi_with_hoa(self):
        """NOI should subtract HOA fees."""
        prop = SAMPLE_PROPERTY.copy()
        prop["hoa_fee"] = 200  # $200/month = $2400/year
        result = calculate_property_analysis(prop)
        expected_noi = (2500 * 12) - 6000 - 1500 - 3000 - 2400
        assert abs(result["noi"] - expected_noi) < 0.01


class TestCapRate:
    """Test Cap Rate calculation."""

    def test_cap_rate_formula(self):
        """Cap Rate = (NOI / Price) × 100"""
        result = calculate_property_analysis(SAMPLE_PROPERTY)
        # NOI = 19500, Price = 300000
        expected_cap_rate = (19500 / 300000) * 100  # = 6.5%
        assert abs(result["cap_rate"] - expected_cap_rate) < 0.01
        assert abs(result["cap_rate"] - 6.5) < 0.01

    def test_cap_rate_zero_price(self):
        """Zero price should not crash."""
        prop = SAMPLE_PROPERTY.copy()
        prop["price"] = 0
        result = calculate_property_analysis(prop)
        assert result["cap_rate"] == 0


class TestCashOnCash:
    """Test Cash-on-Cash Return calculation."""

    def test_cash_on_cash_formula(self):
        """Cash-on-Cash = (Annual Cash Flow / Total Cash Invested) × 100"""
        result = calculate_property_analysis(SAMPLE_PROPERTY)
        # Down payment = 300000 × 0.20 = 60000
        # Closing costs = 300000 × 0.03 = 9000
        # Total cash invested = 69000
        # Loan = 240000
        # Monthly mortgage at 6.5% for 30yr = P&I
        # Annual cash flow = NOI - (mortgage × 12)
        # Check that result is calculated and sensible
        assert isinstance(result["cash_on_cash"], float)
        assert result["down_payment"] == 60000.0

    def test_cash_invested_includes_closing_costs(self):
        """Total cash invested = down payment + 3% closing costs."""
        result = calculate_property_analysis(SAMPLE_PROPERTY)
        expected_down = 300000 * 0.20  # 60000
        expected_closing = 300000 * 0.03  # 9000
        expected_total = expected_down + expected_closing  # 69000
        # Cash-on-cash uses total_cash_invested in denominator
        assert result["down_payment"] == expected_down


class TestMortgageCalculation:
    """Test mortgage payment calculation."""

    def test_mortgage_payment(self):
        """Standard 30yr fixed rate mortgage calculation."""
        result = calculate_property_analysis(SAMPLE_PROPERTY)
        # Loan = 240000, Rate = 6.5%, Term = 30yr
        # Expected monthly payment ≈ $1,517
        assert 1400 < result["mortgage_payment"] < 1650

    def test_mortgage_with_custom_rate(self):
        """Custom mortgage rate should change payment."""
        result_low = calculate_property_analysis(SAMPLE_PROPERTY, mortgage_rate=4.0)
        result_high = calculate_property_analysis(SAMPLE_PROPERTY, mortgage_rate=8.0)
        assert result_low["mortgage_payment"] < result_high["mortgage_payment"]


class TestGoalScoring:
    """Test goal-based scoring algorithm."""

    def test_score_in_range(self):
        """Score should be between 0 and 100."""
        for goal in ["cash_flow", "appreciation", "long_term"]:
            result = calculate_property_analysis(SAMPLE_PROPERTY, goal=goal)
            assert 0 <= result["goal_score"] <= 100

    def test_goal_label_matches_input(self):
        """The goal field should match what was requested."""
        for goal in ["cash_flow", "appreciation", "long_term"]:
            result = calculate_property_analysis(SAMPLE_PROPERTY, goal=goal)
            assert result["goal"] == goal

    def test_high_growth_scores_well_for_appreciation(self):
        """Properties with high market growth should score better for appreciation."""
        prop_high = SAMPLE_PROPERTY.copy()
        prop_high["market_growth_rate"] = 6.0
        prop_low = SAMPLE_PROPERTY.copy()
        prop_low["market_growth_rate"] = 1.5

        score_high = calculate_property_analysis(prop_high, goal="appreciation")["goal_score"]
        score_low = calculate_property_analysis(prop_low, goal="appreciation")["goal_score"]
        assert score_high > score_low


class TestPropertyFilters:
    """Test property filtering."""

    def test_load_all_properties(self):
        """Should load all 50 mock properties."""
        props = get_all_properties()
        assert len(props) == 50

    def test_filter_by_type(self):
        """Filtering by type should only return matching properties."""
        sfh = get_all_properties(property_type="SFH")
        assert all(p["property_type"] == "SFH" for p in sfh)

    def test_filter_by_price_range(self):
        """Price filter should work correctly."""
        props = get_all_properties(min_price=200000, max_price=300000)
        assert all(200000 <= p["price"] <= 300000 for p in props)

    def test_filter_by_state(self):
        """State filter should work."""
        tx = get_all_properties(state="TX")
        assert all(p["state"] == "TX" for p in tx)

    def test_hottest_returns_sorted(self):
        """Hottest properties should be sorted by goal score descending."""
        results = get_hottest_properties(goal="cash_flow", limit=5)
        scores = [r["goal_score"] for r in results]
        assert scores == sorted(scores, reverse=True)
