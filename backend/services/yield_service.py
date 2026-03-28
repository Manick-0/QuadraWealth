"""
QuadraWealth Yield Service
Dynamic yield finder with macro-trigger recommendation logic.
"""
import json
from pathlib import Path


def load_yield_data() -> dict:
    """Load yield vehicles and macro indicators from mock data."""
    data_path = Path(__file__).parent.parent / "data" / "mock_yields.json"
    with open(data_path, "r") as f:
        return json.load(f)


def get_current_yields() -> dict:
    """Return current yields for all vehicles and macro indicators."""
    data = load_yield_data()
    return {
        "macro": data["macro"],
        "vehicles": data["vehicles"],
    }


def recommend_allocation(
    inflation_rate: float = None,
    fed_funds_rate: float = None,
    gdp_growth: float = None,
    risk_tolerance: str = "moderate",
) -> dict:
    """
    Recommend yield vehicle allocations based on macro conditions.

    Logic Tree:
    - High inflation (>3%) → weight gold/commodities higher
    - High rates (>5%) → push cash/short-term bonds
    - Low growth + high rates → treasuries and HYSA (safe haven)
    - Normal conditions → balanced allocation
    - Conservative → more HYSA/T-Bills; Aggressive → more commodities/gold
    """
    data = load_yield_data()
    macro = data["macro"]

    # Override macro with user-provided values (for simulation)
    if inflation_rate is not None:
        macro["inflation_rate"] = inflation_rate
    if fed_funds_rate is not None:
        macro["fed_funds_rate"] = fed_funds_rate
    if gdp_growth is not None:
        macro["gdp_growth"] = gdp_growth

    inf = macro["inflation_rate"]
    rate = macro["fed_funds_rate"]
    gdp = macro["gdp_growth"]

    # ── Base allocations ──
    alloc = {
        "hysa": 20,
        "tbill": 20,
        "bond": 20,
        "gold": 20,
        "commodity": 20,
    }

    rationale_parts = []

    # ── Macro trigger logic tree ──

    # Trigger 1: High inflation → gold & commodities
    if inf > 3.5:
        alloc["gold"] += 15
        alloc["commodity"] += 15
        alloc["bond"] -= 10
        alloc["hysa"] -= 10
        alloc["tbill"] -= 10
        rationale_parts.append(
            f"🔴 Inflation is elevated at {inf}% — overweighting gold and commodities as inflation hedges."
        )
    elif inf > 2.5:
        alloc["gold"] += 8
        alloc["commodity"] += 5
        alloc["bond"] -= 8
        alloc["tbill"] -= 5
        rationale_parts.append(
            f"🟡 Inflation at {inf}% is above target — slightly tilting toward hard assets."
        )
    else:
        alloc["bond"] += 5
        rationale_parts.append(
            f"🟢 Inflation is contained at {inf}% — bonds remain attractive."
        )

    # Trigger 2: High interest rates → cash and short-term
    if rate > 5.0:
        alloc["hysa"] += 12
        alloc["tbill"] += 12
        alloc["bond"] -= 8
        alloc["gold"] -= 8
        alloc["commodity"] -= 8
        rationale_parts.append(
            f"💰 Fed funds rate at {rate}% — locking in high cash yields with HYSA and T-Bills."
        )
    elif rate > 4.0:
        alloc["hysa"] += 5
        alloc["tbill"] += 8
        alloc["bond"] -= 5
        alloc["commodity"] -= 8
        rationale_parts.append(
            f"📊 Rates at {rate}% are elevated — T-Bills offer strong risk-free returns."
        )
    else:
        alloc["bond"] += 8
        alloc["tbill"] -= 5
        alloc["hysa"] -= 3
        rationale_parts.append(
            f"📉 Rates are low at {rate}% — extending duration into bonds for yield."
        )

    # Trigger 3: Growth outlook
    if gdp < 1.5:
        alloc["hysa"] += 10
        alloc["tbill"] += 5
        alloc["commodity"] -= 10
        alloc["gold"] += 5
        alloc["bond"] -= 10
        rationale_parts.append(
            f"⚠️ GDP growth is weak at {gdp}% — prioritizing safety and liquidity."
        )
    elif gdp > 3.0:
        alloc["commodity"] += 8
        alloc["gold"] -= 5
        alloc["hysa"] -= 3
        rationale_parts.append(
            f"🚀 Strong GDP growth at {gdp}% — commodities benefit from economic expansion."
        )

    # ── Risk tolerance adjustment ──
    if risk_tolerance == "conservative":
        alloc["hysa"] += 10
        alloc["tbill"] += 5
        alloc["gold"] -= 8
        alloc["commodity"] -= 7
        rationale_parts.append(
            "🛡️ Conservative profile — tilting toward insured cash and government bonds."
        )
    elif risk_tolerance == "aggressive":
        alloc["gold"] += 5
        alloc["commodity"] += 8
        alloc["hysa"] -= 8
        alloc["tbill"] -= 5
        rationale_parts.append(
            "⚡ Aggressive profile — increasing exposure to gold and commodities for upside."
        )

    # ── Normalize to 100% (no negatives) ──
    for key in alloc:
        alloc[key] = max(alloc[key], 2)  # Minimum 2% in each

    total = sum(alloc.values())
    alloc = {k: round(v / total * 100, 1) for k, v in alloc.items()}

    # Ensure sums to 100
    diff = 100 - sum(alloc.values())
    max_key = max(alloc, key=alloc.get)
    alloc[max_key] = round(alloc[max_key] + diff, 1)

    # ── Top pick ──
    top_vehicle = max(alloc, key=alloc.get)
    category_names = {
        "hysa": "High-Yield Savings Accounts",
        "tbill": "Treasury Bills",
        "bond": "Bonds",
        "gold": "Gold",
        "commodity": "Commodities",
    }

    rationale = " ".join(rationale_parts)
    rationale += f"\n\n📌 **Top Pick: {category_names[top_vehicle]}** ({alloc[top_vehicle]}% allocation)"

    return {
        "macro": macro,
        "vehicles": data["vehicles"],
        "allocations": alloc,
        "rationale": rationale,
    }
