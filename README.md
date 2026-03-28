# 💎 QuadraWealth — Multi-Mode Asset & Capital Manager

> Built for HackUSF 2026 — A 4-mode money manager powered by AI, real-time data, and quantitative analysis.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch everything (backend + frontend)
chmod +x run.sh
./run.sh
```

**Dashboard:** [http://localhost:8501](http://localhost:8501)  
**API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

## 📊 The Four Modes

| Mode | What It Does | Data Source |
|------|-------------|-------------|
| 📈 **Stocks** | RAG-powered equity recommendations | yfinance (live) + ChromaDB |
| 🎯 **The Edge** | Arbitrage & +EV sports betting | The Odds API + mock fallback |
| 🏦 **Savings & Yields** | Macro-driven yield allocation | Mock yield data + simulated macro |
| 🏠 **Real Estate** | Property screener with cap rate analysis | 50 mock properties |

## 🏗️ Architecture

- **Backend:** FastAPI (Python) — async API with auto-generated docs
- **Frontend:** Streamlit — dark-themed, interactive dashboard
- **Database:** SQLite — user profiles and saved leads
- **AI/RAG:** ChromaDB — vector search over financial news for stock recommendations

## 🧪 Run Tests

```bash
pytest backend/tests/ -v
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and add your API keys:

```env
ODDS_API_KEY=your_key_here      # Optional — mock data included
USE_LIVE_ODDS=true               # Set to use live odds data
```

## 📁 Project Structure

```
hackusf/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── routers/             # API endpoints (4 modes)
│   ├── services/            # Business logic + RAG engine
│   ├── models/              # Pydantic schemas + ORM
│   ├── data/                # Mock datasets
│   └── tests/               # Unit tests
├── frontend/
│   ├── app.py               # Streamlit landing page
│   └── pages/               # 4 mode pages
├── run.sh                   # Single-command launcher
└── requirements.txt
```

## 🏆 Team

Built with ❤️ at HackUSF 2026
