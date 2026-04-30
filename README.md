# 💎 QuadraWealth — Multi-Agent AI Capital Manager

> **CIS 4930 — Introduction to Agentic AI | Final Project**  
> University of South Florida · Spring 2026

QuadraWealth is a full-stack **Agentic AI Application** that unifies four investment verticals — Stocks, Sports Betting Edge, Savings Yields, and Real Estate — into a single intelligent platform. A central Orchestrator coordinates a team of specialist AI agents that autonomously reason, call tools, and synthesize cross-asset financial strategies using the **ReAct (Reasoning + Acting)** pattern.

---

## 👥 Team

| Name | USF ID |
|------|--------|
| Manik Jindal | U07146364 |
| Tomas Pastore | |

---

## 📋 Table of Contents

1. [Features](#-features)
2. [System Architecture](#-system-architecture)
3. [Project Structure](#-project-structure)
4. [Requirements](#-requirements)
5. [How to Run](#-how-to-run)
6. [API Keys](#-api-keys-optional)
7. [Usage Guide](#-usage-guide)
8. [Technical Contributions](#-technical-contributions)
9. [Code Sources & Declarations](#-code-sources--declarations)
10. [Grading Checklist](#-grading-checklist)

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 📈 **Stocks** | Live screener with PE, ROE, EPS, EMA200 analysis + RAG-powered news sentiment |
| 🎯 **The Edge** | Real-time arbitrage & +EV bet detection across FanDuel, DraftKings, Hard Rock, PrizePicks |
| 🏦 **Savings Yields** | Macro-driven yield scoring — ranks HYSAs and CDs by risk-adjusted return |
| 🏠 **Real Estate** | Property screener with cap rate, cash-on-cash, and goal-based scoring |
| 🤖 **AI Advisor** | Multi-agent chat — Orchestrator delegates to 4 specialist AI agents in real time |
| 🏛️ **System Architecture** | Visual walkthrough of the full agentic system design |

---

## 🧠 System Architecture

QuadraWealth uses a **Specialist-Orchestrator** multi-agent model:

```
User Query
    │
    ▼
┌─────────────────────────────────┐
│         ORCHESTRATOR            │  ← Plans, delegates, synthesizes
│   (GPT-4o-mini + ReAct Loop)   │
└────┬──────┬──────┬──────┬───── ┘
     │      │      │      │
     ▼      ▼      ▼      ▼
  Market  Risk   Edge  Real Estate
  Agent   Agent  Agent   Agent
     │      │      │      │
     ▼      ▼      ▼      ▼
  yfinance  Macro  Odds   Realty
  ChromaDB  Data   API    API
```

### ReAct Pattern (Per Agent)
Each agent follows a four-step reasoning loop:
1. **THINK** — Analyze the task and identify required data
2. **ACT** — Call the appropriate tool (API / database / service)
3. **OBSERVE** — Process the tool's response
4. **REASON** — Synthesize an answer and report to the Orchestrator

---

## 📁 Project Structure

```
QuadraWealth/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment config & settings
│   ├── database.py              # SQLite connection (quadrawealth.db)
│   ├── agents/
│   │   ├── base.py              # Core ReAct loop logic
│   │   ├── llm.py               # OpenAI GPT-4o-mini client
│   │   ├── memory.py            # Agent memory & shared scratchpad
│   │   ├── orchestrator.py      # Multi-agent planning & synthesis
│   │   ├── market_agent.py      # Stock research specialist
│   │   ├── risk_agent.py        # Macro & yield risk specialist
│   │   ├── edge_agent.py        # Sports betting arbitrage specialist
│   │   └── real_estate_agent.py # Property investment specialist
│   ├── routers/
│   │   ├── stocks.py            # /api/stocks endpoints
│   │   ├── edge.py              # /api/edge endpoints
│   │   ├── yields.py            # /api/yields endpoints
│   │   ├── real_estate.py       # /api/realestate endpoints
│   │   └── agents.py            # /api/agents/chat endpoint
│   ├── services/
│   │   ├── stock_service.py     # yfinance integration
│   │   ├── edge_service.py      # Odds API integration
│   │   ├── yield_service.py     # Yield data service
│   │   └── real_estate_service.py # Real estate data service
│   └── data/
│       └── rag_engine.py        # ChromaDB RAG pipeline
├── frontend/
│   ├── app.py                   # Streamlit home dashboard
│   └── pages/
│       ├── 1_Stocks.py          # Stock screener UI
│       ├── 2_The_Edge.py        # Sports betting UI
│       ├── 3_Savings_Yields.py  # Yield comparison UI
│       ├── 4_Real_Estate.py     # Property screener UI
│       ├── 5_AI_Advisor.py      # Multi-agent chat UI
│       └── 6_System_Architecture.py # Architecture diagram UI
├── chroma_db/                   # Persistent vector store (RAG)
├── quadrawealth.db              # SQLite database
├── requirements.txt             # Python dependencies
├── run.sh                       # One-command launcher
├── .env                         # API keys (not committed)
└── README.md                    # This file
```

---

## 📦 Requirements

- **Python** 3.9 or higher
- **pip3**
- **macOS / Linux / WSL** (Windows users: run via WSL or Git Bash)

All Python dependencies are listed in `requirements.txt`:

```
fastapi
uvicorn
streamlit
openai
yfinance
chromadb
python-dotenv
requests
sqlalchemy
pydantic
```

---

## 🚀 How to Run

### Option 1 — One-Command Launch (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Manick-0/QuadraWealth.git
cd QuadraWealth

# 2. (Optional) Add your API keys
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=your_key_here

# 3. Make the launcher executable and run
chmod +x run.sh
./run.sh
```

The script will automatically install dependencies, start the FastAPI backend on port `8000`, and launch the Streamlit frontend on port `8501`.

### Option 2 — Manual Launch

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Start the backend (in one terminal)
PYTHONPATH=. python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start the frontend (in a second terminal)
PYTHONPATH=. python3 -m streamlit run frontend/app.py --server.port 8501
```

### Access the App

| Interface | URL |
|-----------|-----|
| 📊 Dashboard | http://localhost:8501 |
| 🤖 AI Advisor | http://localhost:8501 → click "AI Advisor" in sidebar |
| 🔌 API Docs (Swagger) | http://localhost:8000/docs |
| ❤️ Health Check | http://localhost:8000/health |

---

## 🔑 API Keys (Optional)

The app runs in **Template Mode** without any API keys (all modules fully functional with cached/simulated data). To enable **Live AI Mode**, add keys to your `.env` file:

```env
OPENAI_API_KEY=your_openai_key      # Enables live GPT-4o-mini reasoning in AI Advisor
ODDS_API_KEY=your_odds_key          # Enables live sportsbook data in The Edge
RAPIDAPI_KEY=your_rapidapi_key      # Enables live real estate listings
```

> **Note:** Never commit your `.env` file. It is already listed in `.gitignore`.

---

## 📖 Usage Guide

### 1. Home Dashboard
- Set your **Risk Tolerance**, **Preferred Sectors**, and **Investment Capital** in the sidebar.
- These profile settings persist across all modules.

### 2. Stocks
- Click **Stocks** in the sidebar.
- The screener fetches live data and ranks tickers by composite score (fundamentals + momentum + RAG sentiment).

### 3. The Edge
- Click **The Edge**.
- View arbitrage opportunities and +EV bets with implied probability and edge percentage.

### 4. Savings Yields
- Click **Savings Yields**.
- Compare high-yield savings accounts and CDs, ranked by macro-adjusted return score.

### 5. Real Estate
- Click **Real Estate**.
- Filter properties by location and budget. View cap rate, cash-on-cash return, and AI score.

### 6. AI Advisor (Multi-Agent Chat)
- Click **AI Advisor**.
- Type any cross-asset question, for example:
  > *"I have $10,000. How should I split it across stocks, real estate, and savings given moderate risk?"*
- Watch the Orchestrator plan the task, delegate to specialist agents, and stream a unified response.

---

## 🛠️ Technical Contributions

| Contribution | Description |
|---|---|
| **Multi-Agent Orchestration** | Custom Orchestrator that plans, delegates, and synthesizes across 4 specialist agents |
| **ReAct Loop Implementation** | Each agent implements Think → Act → Observe → Reason from scratch in Python |
| **RAG Pipeline** | ChromaDB vector store ingests financial news; agents query it for grounded sentiment |
| **Tool Calling Schema** | All backend services exposed as JSON-schema-defined tools callable by the LLM |
| **Shared Agent Memory** | Cross-agent scratchpad allows specialists to share intermediate findings |
| **Async Timeout Guards** | All agent API calls wrapped with `asyncio.wait_for` to prevent UI hangs |
| **Four Live Data Modules** | Stock screener, odds/arbitrage engine, yield ranker, and real estate screener |
| **Full-Stack Integration** | FastAPI backend + Streamlit frontend with live streaming agent responses |

---

## 📣 Code Sources & Declarations

In accordance with course policy, all external libraries and data sources used are declared below:

| Source | Usage | License |
|--------|-------|---------|
| [OpenAI Python SDK](https://github.com/openai/openai-python) | GPT-4o-mini API calls for LLM reasoning | MIT |
| [yfinance](https://github.com/ranaroussi/yfinance) | Real-time and historical stock market data | Apache 2.0 |
| [ChromaDB](https://github.com/chroma-core/chroma) | Vector database for RAG news retrieval | Apache 2.0 |
| [FastAPI](https://fastapi.tiangolo.com/) | Async REST API framework | MIT |
| [Streamlit](https://streamlit.io/) | Frontend dashboard framework | Apache 2.0 |
| [The Odds API](https://the-odds-api.com/) | Live sportsbook odds for arbitrage detection | Commercial (free tier) |
| [RapidAPI / Realty API](https://rapidapi.com/) | Real estate property listings | Commercial (free tier) |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM for SQLite database | MIT |

> **All application logic, agent architectures, ReAct implementations, prompt engineering, tool schemas, and system design were written by the project team.** No code was copied from external repositories or AI-generated wholesale. Libraries above were used as documented dependencies only.

---

## ✅ Grading Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Code uploaded to GitHub | ✅ | [github.com/Manick-0/QuadraWealth](https://github.com/Manick-0/QuadraWealth) |
| Files properly organized and documented | ✅ | See [Project Structure](#-project-structure) above; all modules have docstrings |
| README with clear run instructions | ✅ | See [How to Run](#-how-to-run) section above |
| Code sources declared | ✅ | See [Code Sources & Declarations](#-code-sources--declarations) above |
| Functional code / working application | ✅ | FastAPI backend + Streamlit frontend, both locally runnable |
| Multi-Agent AI system | ✅ | Orchestrator + 4 specialist agents with ReAct loops |
| LLM Integration | ✅ | GPT-4o-mini via OpenAI SDK |
| RAG Integration | ✅ | ChromaDB vector store for financial news retrieval |
| User Experience | ✅ | Premium dark-theme Streamlit dashboard with live streaming |
| Technical documentation | ✅ | Architecture diagrams, component tables, docstrings throughout |

---

Built for **CIS 4930 — Introduction to Agentic AI** · University of South Florida · Spring 2026
