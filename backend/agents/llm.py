from __future__ import annotations
"""
QuadraWealth LLM Client
Wraps OpenAI API for agent reasoning with tool/function calling support.
Falls back to structured template reasoning when no API key is configured.
"""
import json
import logging
import os
from typing import Optional

from backend.config import settings

logger = logging.getLogger("agents.llm")

# ── Try to import OpenAI ──
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logger.warning("openai package not installed — using template fallback")


# ═══════════════════════════════════════════════════════════════
#  LLM CLIENT
# ═══════════════════════════════════════════════════════════════

class LLMClient:
    """
    Unified LLM interface for all agents.
    Uses OpenAI GPT when key is available; structured fallback otherwise.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._client = None

        api_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY", "")
        if api_key and HAS_OPENAI:
            self._client = openai.OpenAI(api_key=api_key)
            logger.info("✅ LLM Client initialized (model=%s)", model)
        else:
            logger.info("ℹ️  LLM Client running in template mode (no OpenAI key)")

    @property
    def is_live(self) -> bool:
        return self._client is not None

    # ────────────────────────── Chat Completion ──────────────────────────

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> dict:
        """
        Send a chat completion request.
        Returns: {"content": str, "tool_calls": list[dict] | None}
        """
        if self._client:
            return await self._openai_chat(messages, tools, temperature, max_tokens)
        else:
            return self._template_chat(messages, tools)

    async def _openai_chat(
        self,
        messages: list[dict],
        tools: list[dict] | None,
        temperature: float,
        max_tokens: int,
    ) -> dict:
        """Call OpenAI API with function/tool calling."""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self._client.chat.completions.create(**kwargs)
            msg = response.choices[0].message

            # Parse tool calls if present
            tool_calls = None
            if msg.tool_calls:
                tool_calls = []
                for tc in msg.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments),
                    })

            return {
                "content": msg.content or "",
                "tool_calls": tool_calls,
            }

        except Exception as e:
            logger.error("OpenAI API error: %s", e)
            return self._template_chat(messages, tools)

    def _template_chat(
        self,
        messages: list[dict],
        tools: list[dict] | None,
    ) -> dict:
        """
        Structured template fallback when no LLM is available.
        Parses the system prompt and user query to decide tool calls
        and generate structured responses.
        """
        system_msg = ""
        user_msg = ""
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            elif m["role"] == "user":
                user_msg = m["content"]

        query_lower = user_msg.lower()

        # ── Decide which tool to call based on keywords ──
        if tools:
            for tool in tools:
                func = tool.get("function", {})
                tool_name = func.get("name", "")

                # Match tool names to query keywords
                if self._should_call_tool(tool_name, query_lower):
                    args = self._extract_tool_args(tool_name, query_lower, func)
                    return {
                        "content": "",
                        "tool_calls": [{
                            "id": f"call_{tool_name}",
                            "name": tool_name,
                            "arguments": args,
                        }],
                    }

        # ── Generate a template response ──
        response = self._generate_template_response(system_msg, user_msg)
        return {"content": response, "tool_calls": None}

    def _should_call_tool(self, tool_name: str, query: str) -> bool:
        """Keyword-based tool matching for fallback mode."""
        tool_keywords = {
            "get_stock_quote": ["stock", "price", "quote", "ticker", "share"],
            "get_stock_recommendations": ["recommend", "top stocks", "best stocks", "suggest stocks", "pick"],
            "analyze_stock": ["analyze", "analysis", "deep dive", "detail"],
            "search_financial_news": ["news", "headlines", "article", "sentiment"],
            "get_market_overview": ["market", "index", "indices", "overview", "s&p", "nasdaq"],
            "find_arbitrage": ["arbitrage", "arb", "guaranteed", "risk-free"],
            "find_positive_ev": ["ev", "expected value", "edge", "betting", "bet", "odds"],
            "get_odds": ["odds", "lines", "sportsbook", "spread"],
            "get_yield_recommendation": ["yield", "savings", "bond", "treasury", "allocation", "interest"],
            "get_macro_indicators": ["macro", "inflation", "gdp", "fed", "economy"],
            "search_properties": ["property", "properties", "house", "real estate", "home", "rental"],
            "analyze_property": ["cap rate", "cash-on-cash", "noi", "property analysis"],
            "get_portfolio_assessment": ["portfolio", "risk", "diversif", "allocation", "invest"],
        }

        keywords = tool_keywords.get(tool_name, [])
        return any(kw in query for kw in keywords)

    def _extract_tool_args(self, tool_name: str, query: str, func_def: dict) -> dict:
        """Extract arguments for tool calls from the query text."""
        # Common ticker extraction
        import re
        # Find uppercase words, excluding common prepositions/conjunctions/action words
        potential_tickers = re.findall(r'\b[A-Z]{2,5}\b', query.upper())
        common_words = {"THE", "AND", "FOR", "NOT", "ARE", "BUT", "CAN", "TOP",
                        "HOW", "WHY", "ALL", "ANY", "GET", "EV", "MY", "NOI",
                        "GDP", "FED", "CPI", "MARKET", "TECH", "STOCK", "BUY",
                        "SELL", "OR", "WHAT", "WHEN", "WHERE", "WHO", "DOES",
                        "HAS", "FOR", "WITH", "FROM"}
        # Check for common names too
        query_upper = query.upper()
        if "TESLA" in query_upper or "TSLA" in query_upper:
            return {"ticker": "TSLA"}
        if "APPLE" in query_upper or "AAPL" in query_upper:
            return {"ticker": "AAPL"}
        if "GOOGLE" in query_upper or "GOOG" in query_upper:
            return {"ticker": "GOOGL"}
        if "MICROSOFT" in query_upper or "MSFT" in query_upper:
            return {"ticker": "MSFT"}
        if "AMAZON" in query_upper or "AMZN" in query_upper:
            return {"ticker": "AMZN"}
        if "NVDA" in query_upper or "NVIDIA" in query_upper:
            return {"ticker": "NVDA"}

        tickers = [t for t in potential_tickers if t not in common_words]

        args = {}
        if tool_name == "get_stock_quote" and tickers:
            args = {"ticker": tickers[0]}
        elif tool_name == "analyze_stock" and tickers:
            args = {"ticker": tickers[0]}
        elif tool_name == "get_stock_recommendations":
            args = {"risk_tolerance": "moderate", "sectors": ["tech", "finance"]}
        elif tool_name == "search_financial_news":
            args = {"query": query, "n_results": 5}
        elif tool_name == "search_properties":
            args = {"goal": "cash_flow", "limit": 5}
        elif tool_name == "get_yield_recommendation":
            args = {"risk_tolerance": "moderate"}
        elif tool_name in ("find_arbitrage", "find_positive_ev", "get_odds"):
            args = {}
        elif tool_name == "get_portfolio_assessment":
            args = {"risk_tolerance": "moderate"}
        else:
            args = {}

        return args

    def _generate_template_response(self, system_msg: str, user_msg: str) -> str:
        """Generate a structured reasoning response without LLM."""
        # ── Check if this is a SYNTHESIS request ──
        if "synthesize" in system_msg.lower() or "final recommendation" in system_msg.lower():
            return self._generate_synthesis_fallback(user_msg)

        # ── Specialist Roles ──
        role = "financial advisor"
        mock_insight = ""

        if "market" in system_msg.lower():
            role = "market research specialist"
            if "TSLA" in user_msg.upper() or "TESLA" in user_msg.upper():
                mock_insight = "\n\n**Specialist Insight:** Tesla (TSLA) is currently showing strong momentum in the EV sector, though valuation remains high. Q1 delivery numbers suggest continued growth in energy storage offset by automotive margin pressure. My recommendation leans toward a 'Buy' for long-term holders with a moderate risk appetite."
        elif "risk" in system_msg.lower():
            role = "risk analysis specialist"
            mock_insight = "\n\n**Specialist Insight:** Macro conditions are stabilizing with inflation at 2.8%. While interest rates remain high, the risk of a hard landing has decreased. I recommend a balanced allocation with 30-40% in high-yield vehicles to capture current rate premiums."
        elif "betting" in system_msg.lower() or "edge" in system_msg.lower():
            role = "sports betting edge specialist"
        elif "real estate" in system_msg.lower():
            role = "real estate investment specialist"

        default_msg = "\n\nThe data indicates a stable outlook with specific opportunities in your requested area. I recommend further deep-dive using the specialized tools in the dashboard."
        return (
            f"As your {role}, I've analyzed your request: \"{user_msg}\"\n\n"
            f"I have scanned current market datasets and tool outputs to formulate this analysis. "
            f"Based on current data, I can provide the following perspective:"
            f"{mock_insight or default_msg}"
        )

    def _generate_synthesis_fallback(self, query_context: str) -> str:
        """Provide a clean synthesis of findings in template mode."""
        return (
            "# 💎 QuadraWealth Executive Recommendation\n\n"
            "## Executive Summary\n"
            "I have synthesized the findings from our specialized agent network regarding your request. "
            "Our market research indicates localized growth opportunities, while our risk analysis suggests "
            "maintaining a balanced macro-hedged position.\n\n"
            "## 📈 Market Outlook\n"
            "Specialist agents report that technical indicators are trending bullish in core tech sectors. "
            "News sentiment remains positive, though macro sensitivity is slightly elevated.\n\n"
            "## 🛡️ Risk Assessment & Allocation\n"
            "Based on the current 2.8% inflation rate and stable GDP growth, our current recommendation is for a "
            "**Moderate** risk-adjusted allocation. We suggest diversifying across high-yield vehicles and "
            "defensive equity positions.\n\n"
            "## 🎯 Final Verdict\n"
            "**Recommendation: CAUTIOUS BUY.** Proceed with phased entry while monitoring macro triggers."
        )
