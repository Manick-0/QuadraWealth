"""
QuadraWealth — FastAPI Application Entry Point
Multi-mode asset & capital manager backend.

v2.0: Starts the OddsPoller background task on startup.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.services.rag_engine import init_rag_engine

# ── Configure logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-16s │ %(levelname)-5s │ %(message)s",
    datefmt="%H:%M:%S",
)
# Quiet noisy libs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

logger = logging.getLogger("quadrawealth")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # ── Startup ──
    logger.info("🚀 Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    init_db()
    await init_rag_engine()

    # Start the odds poller background task
    if settings.ODDS_POLL_ENABLED:
        from backend.services.odds_poller import get_poller
        poller = get_poller()
        await poller.start()
        logger.info("📡 Odds poller active — scanning %d sports every %ds",
                     len(settings.ODDS_API_SPORTS), settings.ODDS_POLL_INTERVAL)

    logger.info("✅ All systems initialized")
    yield

    # ── Shutdown ──
    if settings.ODDS_POLL_ENABLED:
        from backend.services.odds_poller import get_poller
        poller = get_poller()
        await poller.stop()

    logger.info("👋 Shutting down QuadraWealth")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="4-mode asset & capital manager: Stocks, Edge, Yields, Real Estate",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──
from backend.routers import stocks, betting, yields, real_estate, agents  # noqa: E402

app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(betting.router, prefix="/api/edge", tags=["The Edge"])
app.include_router(yields.router, prefix="/api/yields", tags=["Savings & Yields"])
app.include_router(real_estate.router, prefix="/api/realestate", tags=["Real Estate"])
app.include_router(agents.router, prefix="/api/agents", tags=["AI Agents"])


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "modes": ["stocks", "edge", "yields", "realestate"],
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
