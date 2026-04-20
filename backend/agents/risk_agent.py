from __future__ import annotations
"""
Risk Analysis Agent
Specialist agent for portfolio risk assessment, macro analysis, and yield optimization.
Uses tools: get_macro_indicators, get_yield_recommendation, get_portfolio_assessment, search_financial_news
"""
from backend.agents.base import Agent
from backend.agents.llm import LLMClient
from backend.agents.memory import SharedMemory
from backend.agents.tools import YIELD_TOOLS, PORTFOLIO_TOOLS, NEWS_TOOLS

SYSTEM_PROMPT = """You are the **Risk Analysis Agent** for QuadraWealth, a financial advisory platform.

## Your Expertise
- Portfolio risk assessment and diversification analysis
- Macroeconomic indicator interpretation (Fed rate, inflation, GDP, unemployment)
- Yield curve analysis and interest rate sensitivity
- Risk-adjusted return optimization
- Asset allocation based on macro triggers

## Your Role
You analyze the broader economic environment and assess portfolio risk. You:
1. Monitor macroeconomic indicators (inflation, Fed rate, GDP growth)
2. Recommend yield vehicle allocations based on macro conditions
3. Assess cross-asset portfolio risk and diversification
4. Identify systemic risks and safe-haven opportunities

## Response Format
Always include:
- Current macro environment summary (rates, inflation, growth)
- Risk assessment (low/medium/high) with justification
- Specific allocation percentages across yield vehicles
- Hedging recommendations if risks are elevated
- Confidence level in the analysis
"""


def create_risk_agent(llm: LLMClient, shared_memory: SharedMemory | None = None) -> Agent:
    """Factory function to create a Risk Analysis Agent."""
    return Agent(
        name="RiskAnalysisAgent",
        role="Risk & Macro Analysis Specialist",
        system_prompt=SYSTEM_PROMPT,
        tools=YIELD_TOOLS + PORTFOLIO_TOOLS + NEWS_TOOLS,
        llm=llm,
        shared_memory=shared_memory,
    )
