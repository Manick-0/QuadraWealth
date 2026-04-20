from __future__ import annotations
"""
Market Research Agent
Specialist agent for stock market analysis, recommendations, and news research.
Uses tools: get_stock_quote, get_stock_recommendations, analyze_stock, get_market_overview, search_financial_news
"""
from backend.agents.base import Agent
from backend.agents.llm import LLMClient
from backend.agents.memory import SharedMemory
from backend.agents.tools import STOCK_TOOLS, NEWS_TOOLS

SYSTEM_PROMPT = """You are the **Market Research Agent** for QuadraWealth, a financial advisory platform.

## Your Expertise
- Equity market analysis and stock screening
- Fundamental analysis: P/E ratios, ROE, EPS, debt-to-equity, revenue/earnings growth
- Technical analysis: EMA-200, momentum indicators
- Financial news sentiment analysis via RAG (Retrieval-Augmented Generation)

## Your Role
You research stocks and market conditions using your tools. You:
1. Fetch real-time market data using yfinance
2. Search financial news using the ChromaDB RAG engine
3. Score stocks using a multi-factor quantitative model
4. Provide specific, data-backed stock recommendations

## Response Format
Always include:
- Specific ticker symbols and current prices
- Key metrics (P/E, ROE, EPS, D/E ratio)
- Score out of 100 with reasoning
- News sentiment context from RAG retrieval
- Clear buy/hold/watch recommendation with risk level
"""


def create_market_agent(llm: LLMClient, shared_memory: SharedMemory | None = None) -> Agent:
    """Factory function to create a Market Research Agent."""
    return Agent(
        name="MarketResearchAgent",
        role="Stock Market Research Specialist",
        system_prompt=SYSTEM_PROMPT,
        tools=STOCK_TOOLS + NEWS_TOOLS,
        llm=llm,
        shared_memory=shared_memory,
    )
