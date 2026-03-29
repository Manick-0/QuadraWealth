"""
QuadraWealth Configuration
Centralized settings with environment variable support and fallback defaults.
"""
import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # App
    APP_NAME: str = "QuadraWealth"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # Server
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./quadrawealth.db"
    SYNC_DATABASE_URL: str = "sqlite:///./quadrawealth.db"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # API Keys
    ODDS_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    RAPIDAPI_KEY: str = ""  # For Realty Mole Property API on RapidAPI

    # Feature Flags — controls live API vs mock data
    USE_LIVE_ODDS: bool = True  # Will auto-fall back to mock if no API key
    USE_LIVE_STOCKS: bool = True  # yfinance is free, default to live
    USE_LIVE_REALESTATE: bool = True  # Uses Realty Mole API via RapidAPI

    # ── Odds Poller Configuration ──
    ODDS_POLL_INTERVAL: int = 300       # Seconds between polls (pre-match) — conserve API credits
    ODDS_POLL_LIVE_INTERVAL: int = 120  # Seconds between polls (live events)
    ODDS_POLL_ENABLED: bool = True      # Enable background polling

    # ── Arb / EV Thresholds ──
    ARB_MIN_PROFIT_PCT: float = 0.1     # Min arb % to report (filters noise)
    EV_MIN_EDGE_PCT: float = 2.0        # Min +EV edge % to report

    # The Odds API
    ODDS_API_BASE_URL: str = "https://api.the-odds-api.com/v4"
    ODDS_API_REGIONS: str = "us"
    ODDS_API_MARKETS: str = "h2h,spreads,totals"
    ODDS_API_BOOKMAKERS: list[str] = [
        "fanduel",
        "draftkings",
        "hardrockbet",
        "prizepicks",
        "betmgm",
        "caesars",
    ]
    ODDS_API_SPORTS: list[str] = [
        "basketball_nba",
        "baseball_mlb",
    ]

    # yfinance defaults
    DEFAULT_WATCHLIST: list[str] = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
        "JPM", "V", "JNJ", "PG", "XOM", "UNH", "HD", "KO",
        "PFE", "BAC", "DIS", "NFLX", "AMD",
    ]

    # Backend URL for frontend to call
    BACKEND_URL: str = "http://localhost:8000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


# Singleton
settings = Settings()
