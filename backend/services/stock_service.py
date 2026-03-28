"""
QuadraWealth Stock Service
yfinance integration, portfolio simulation, and RAG-powered recommendations.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional

from backend.config import settings
from backend.services.rag_engine import query_relevant_news
from backend.models.schemas import (
    StockQuote, StockRecommendation, MarketOverview, PortfolioPositionSchema,
)


# ─── Sector mapping for RAG queries ─────────────────────
SECTOR_MAP = {
    "tech": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD", "NFLX"],
    "finance": ["JPM", "V", "BAC"],
    "healthcare": ["JNJ", "UNH", "PFE"],
    "consumer": ["PG", "HD", "KO", "DIS"],
    "energy": ["XOM"],
}

RISK_VOLATILITY_MAP = {
    "conservative": (0, 25),     # low beta / volatility stocks
    "moderate": (10, 40),
    "aggressive": (20, 100),
}

INDEX_TICKERS = ["^GSPC", "^IXIC", "^DJI"]
INDEX_NAMES = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "Dow Jones"}


def _safe_get(info: dict, key: str, default=None):
    """Safely get a value from yfinance info dict."""
    try:
        val = info.get(key, default)
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        return val
    except Exception:
        return default


def get_stock_quote(ticker: str) -> Optional[StockQuote]:
    """Fetch a real-time quote for a single ticker."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="2d")

        if hist.empty:
            return None

        current_price = float(hist["Close"].iloc[-1])
        prev_price = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price * 100) if prev_price != 0 else 0

        return StockQuote(
            ticker=ticker,
            name=_safe_get(info, "shortName", ticker),
            price=round(current_price, 2),
            change=round(change, 2),
            change_pct=round(change_pct, 2),
            volume=int(_safe_get(info, "volume", 0)),
            market_cap=_safe_get(info, "marketCap"),
            pe_ratio=_safe_get(info, "trailingPE"),
            dividend_yield=_safe_get(info, "dividendYield"),
            sector=_safe_get(info, "sector", "Unknown"),
            week52_high=_safe_get(info, "fiftyTwoWeekHigh"),
            week52_low=_safe_get(info, "fiftyTwoWeekLow"),
        )
    except Exception as e:
        print(f"⚠️ Error fetching {ticker}: {e}")
        return None


def get_market_overview() -> dict:
    """Get market indices and top movers from the watchlist."""
    indices = []
    for idx_ticker in INDEX_TICKERS:
        try:
            t = yf.Ticker(idx_ticker)
            hist = t.history(period="2d")
            if not hist.empty:
                current = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
                change = current - prev
                indices.append(StockQuote(
                    ticker=idx_ticker,
                    name=INDEX_NAMES.get(idx_ticker, idx_ticker),
                    price=round(current, 2),
                    change=round(change, 2),
                    change_pct=round(change / prev * 100 if prev else 0, 2),
                    volume=0,
                ))
        except Exception:
            pass

    # Fetch watchlist quotes
    quotes = []
    for ticker in settings.DEFAULT_WATCHLIST[:10]:  # Limit for speed
        q = get_stock_quote(ticker)
        if q:
            quotes.append(q)

    # Sort by change %
    quotes.sort(key=lambda x: x.change_pct, reverse=True)
    top_gainers = [q for q in quotes if q.change_pct > 0][:5]
    top_losers = sorted([q for q in quotes if q.change_pct <= 0], key=lambda x: x.change_pct)[:5]

    return {
        "indices": [i.model_dump() for i in indices],
        "top_gainers": [g.model_dump() for g in top_gainers],
        "top_losers": [l.model_dump() for l in top_losers],
    }


def get_recommendations(
    risk_tolerance: str = "moderate",
    preferred_sectors: list[str] | None = None,
    capital: float = 10000.0,
) -> list[dict]:
    """
    Generate RAG-powered stock recommendations.
    Uses ChromaDB to find relevant news, then scores stocks
    based on profile match + news sentiment.
    """
    if preferred_sectors is None:
        preferred_sectors = ["tech", "finance"]

    recommendations = []

    for sector in preferred_sectors:
        tickers = SECTOR_MAP.get(sector, [])
        if not tickers:
            continue

        # Query RAG for sector-relevant news
        news_context = query_relevant_news(
            query_text=f"Latest {sector} sector investment opportunities and risks",
            n_results=3,
            sector_filter=sector,
        )

        # Determine sentiment bias from news
        bullish_count = sum(1 for n in news_context if n.get("sentiment") == "bullish")
        bearish_count = sum(1 for n in news_context if n.get("sentiment") == "bearish")
        sector_sentiment = "bullish" if bullish_count > bearish_count else (
            "bearish" if bearish_count > bullish_count else "neutral"
        )

        for ticker in tickers[:4]:  # Top 4 per sector for richer results
            try:
                t = yf.Ticker(ticker)
                info = t.info
                hist = t.history(period="3mo")

                if hist.empty or len(hist) < 5:
                    continue

                current_price = float(hist["Close"].iloc[-1])
                month_start = float(hist["Close"].iloc[0])
                momentum = (current_price - month_start) / month_start * 100

                # ── Enhanced Scoring Algorithm ──
                score = 50  # Base score
                signals = []

                # 1. Sector match bonus
                score += 8
                signals.append("sector_match")

                # 2. Multi-period momentum
                if len(hist) >= 20:
                    short_momentum = (current_price - float(hist["Close"].iloc[-5])) / float(hist["Close"].iloc[-5]) * 100
                else:
                    short_momentum = momentum

                if momentum > 8 and short_momentum > 0:
                    score += 15
                    signals.append("strong_momentum")
                elif momentum > 3:
                    score += 10
                    signals.append("positive_momentum")
                elif momentum > 0:
                    score += 5
                    signals.append("mild_uptrend")
                elif momentum < -8:
                    score -= 12
                    signals.append("negative_momentum")
                elif momentum < 0:
                    score -= 5
                    signals.append("mild_downtrend")

                # 3. Risk alignment
                pe = _safe_get(info, "trailingPE", 20)
                beta = _safe_get(info, "beta", 1.0)
                if risk_tolerance == "conservative" and beta and beta < 1.0:
                    score += 10
                    signals.append("low_volatility")
                elif risk_tolerance == "aggressive" and beta and beta > 1.2:
                    score += 10
                    signals.append("high_growth_potential")
                elif risk_tolerance == "moderate" and beta and 0.8 <= beta <= 1.3:
                    score += 7
                    signals.append("balanced_risk")

                # 4. Value check (P/E analysis)
                if pe and pe > 0:
                    if pe < 15:
                        score += 10
                        signals.append("deep_value")
                    elif pe < 25:
                        score += 6
                        signals.append("value_play")
                    elif pe > 50:
                        score -= 8
                        signals.append("high_valuation")
                    elif pe > 35:
                        score -= 3
                        signals.append("elevated_valuation")

                # 5. News sentiment boost (RAG-powered)
                if sector_sentiment == "bullish":
                    score += 12
                    signals.append("positive_news_sentiment")
                elif sector_sentiment == "bearish":
                    score -= 8
                    signals.append("cautious_news_sentiment")

                # 6. Dividend check
                div_yield = _safe_get(info, "dividendYield", 0) or 0
                if risk_tolerance == "conservative" and div_yield > 0.02:
                    score += 8
                    signals.append("dividend_payer")
                elif div_yield > 0.04:
                    score += 5
                    signals.append("high_dividend")

                # 7. 52-week proximity analysis
                w52_high = _safe_get(info, "fiftyTwoWeekHigh")
                w52_low = _safe_get(info, "fiftyTwoWeekLow")
                if w52_high and w52_low and w52_high > w52_low:
                    range_pct = (current_price - w52_low) / (w52_high - w52_low)
                    if range_pct < 0.3:
                        score += 8
                        signals.append("near_52w_low")
                    elif range_pct > 0.9:
                        score -= 4
                        signals.append("near_52w_high")

                # 8. Volatility analysis (simple Sharpe-like)
                if len(hist) >= 20:
                    daily_returns = hist["Close"].pct_change().dropna()
                    volatility = float(daily_returns.std()) * (252 ** 0.5)  # Annualized
                    if volatility < 0.25:
                        score += 5
                        signals.append("low_vol")
                    elif volatility > 0.6:
                        if risk_tolerance != "aggressive":
                            score -= 5
                            signals.append("high_vol")

                # 9. Volume spike detection
                avg_vol = _safe_get(info, "averageVolume", 0) or 0
                if avg_vol > 0 and len(hist) >= 5:
                    recent_vol = float(hist["Volume"].iloc[-5:].mean())
                    if recent_vol > avg_vol * 1.5:
                        score += 5
                        signals.append("volume_surge")

                score = max(0, min(100, score))

                # Build rich reasoning from RAG context
                news_summary = "; ".join([n["text"][:80] + "..." for n in news_context[:2]])
                reasoning_parts = [f"Composite score: {score}/100."]
                reasoning_parts.append(f"3-month momentum: {momentum:+.1f}%.")
                reasoning_parts.append(f"Sector outlook: {sector_sentiment}.")
                if pe and pe > 0:
                    reasoning_parts.append(f"P/E ratio: {pe:.1f}.")
                if beta:
                    reasoning_parts.append(f"Beta: {beta:.2f}.")
                if div_yield > 0:
                    reasoning_parts.append(f"Dividend yield: {div_yield*100:.2f}%.")
                if news_summary:
                    reasoning_parts.append(f"News context: {news_summary}")

                reasoning = " ".join(reasoning_parts)
                risk_level = "low" if beta and beta < 0.8 else ("high" if beta and beta > 1.3 else "medium")

                recommendations.append({
                    "ticker": ticker,
                    "name": _safe_get(info, "shortName", ticker),
                    "price": round(current_price, 2),
                    "score": score,
                    "reasoning": reasoning,
                    "risk_level": risk_level,
                    "sector": sector,
                    "signals": signals,
                })
            except Exception as e:
                print(f"⚠️ Error analyzing {ticker}: {e}")

    # Sort by score descending
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    return recommendations


def analyze_stock(ticker: str) -> dict:
    """Deep-dive analysis of a single stock."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="6mo")

        if hist.empty:
            return {"error": f"No data for {ticker}"}

        current = float(hist["Close"].iloc[-1])

        # Get relevant news from RAG
        sector = _safe_get(info, "sector", "general").lower()
        news = query_relevant_news(
            query_text=f"{ticker} {_safe_get(info, 'shortName', ticker)} stock analysis",
            n_results=3,
            sector_filter=sector if sector in SECTOR_MAP else None,
        )

        return {
            "quote": {
                "ticker": ticker,
                "name": _safe_get(info, "shortName", ticker),
                "price": round(current, 2),
                "sector": _safe_get(info, "sector", "Unknown"),
                "pe_ratio": _safe_get(info, "trailingPE"),
                "forward_pe": _safe_get(info, "forwardPE"),
                "market_cap": _safe_get(info, "marketCap"),
                "dividend_yield": _safe_get(info, "dividendYield"),
                "beta": _safe_get(info, "beta"),
                "week52_high": _safe_get(info, "fiftyTwoWeekHigh"),
                "week52_low": _safe_get(info, "fiftyTwoWeekLow"),
                "avg_volume": _safe_get(info, "averageVolume"),
            },
            "history": {
                "dates": hist.index.strftime("%Y-%m-%d").tolist(),
                "close": hist["Close"].round(2).tolist(),
                "volume": hist["Volume"].tolist(),
            },
            "relevant_news": news,
        }
    except Exception as e:
        return {"error": str(e)}
