"""
QuadraWealth — FastAPI Application Entry Point
Multi-mode asset & capital manager backend.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.services.rag_engine import init_rag_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # ── Startup ──
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    await init_rag_engine()
    print("✅ All systems initialized")
    yield
    # ── Shutdown ──
    print("👋 Shutting down QuadraWealth")


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
from backend.routers import stocks, betting, yields, real_estate  # noqa: E402

app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(betting.router, prefix="/api/edge", tags=["The Edge"])
app.include_router(yields.router, prefix="/api/yields", tags=["Savings & Yields"])
app.include_router(real_estate.router, prefix="/api/realestate", tags=["Real Estate"])


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
