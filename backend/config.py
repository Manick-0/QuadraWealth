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
    APP_VERSION: str = "1.0.0"
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

    # Feature Flags — controls live API vs mock data
    USE_LIVE_ODDS: bool = True  # Will auto-fall back to mock if no API key
    USE_LIVE_STOCKS: bool = True  # yfinance is free, default to live
    USE_LIVE_ZILLOW: bool = False  # Mock only (Zillow API requires paid RapidAPI)

    # The Odds API
    ODDS_API_BASE_URL: str = "https://api.the-odds-api.com/v4"
    ODDS_API_REGIONS: str = "us"
    ODDS_API_MARKETS: str = "h2h,spreads,totals"
    ODDS_API_BOOKMAKERS: list[str] = [
        "fanduel",
        "draftkings",
        "hardrockbet",
        "prizepicks",
    ]
    ODDS_API_SPORTS: list[str] = [
        "basketball_nba",
        "americanfootball_nfl",
        "baseball_mlb",
        "cricket_ipl",  # T20 cricket (IPL is biggest T20 league)
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
