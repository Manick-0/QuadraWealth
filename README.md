# 💎 QuadraWealth — Multi-Agent AI Capital Manager

> **CIS 4930 (Introduction to Agentic AI) Final Project**

QuadraWealth is an advanced **Agentic AI Application** designed to automate complex financial research, asset allocation, and opportunity detection. It moves beyond traditional "if-then" logic by utilizing an **autonomous multi-agent system** that thinks, plans, and calls tools to solve multi-faceted capital management problems.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Add your API keys to .env (Optional but Recommended for "Live AI")
# OPENAI_API_KEY=your_key_here
# ODDS_API_KEY=your_key_here

# 3. Launch everything
chmod +x run.sh
./run.sh
```

**Dashboard:** [http://localhost:8501](http://localhost:8501)  
**AI Advisor:** [http://localhost:8501/AI_Advisor](http://localhost:8501/AI_Advisor)  
**API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🤖 Agentic AI Architecture (The "Brain")

QuadraWealth doesn't just display data; it **reasons** about it. The system is built on a **Specialist-Orchestrator** model.

### 🧠 1. The Orchestrator (Executive Planning)
When a user asks a question (e.g., *"Is it a good time to buy tech stocks and should I hedge with gold?"*), the Orchestrator performs:
1.  **Planning:** It decomposes the query into sub-tasks (Stock Research + Macro Risk Assessment).
2.  **Delegation:** It dispatches these tasks to the relevant specialist agents concurrently.
3.  **Synthesis:** It gathers all specialist reports, reconciles conflicting data, and writes a cohesive final recommendation.

### 🛰️ 2. Specialist Agents (Domain Experts)
Each agent is a specialized "worker" with its own tools and persona:
- **📈 Market Research Agent:** Specialist in technicals ($AAPL price, P/E ratios) and RAG news sentiment.
- **🛡️ Risk Analysis Agent:** Specialist in macroeconomics (Fed rates, CPI) and optimal yield weighting.
- **🎯 Edge Agent:** Specialist in mathematical betting arbitrage and +EV detection across sportsbooks.
- **🏠 Real Estate Agent:** Specialist in investment property modeling (Cap Rates, Cash-on-Cash returns).

---

## 👁️ The "ReAct" Thinking Process
Every agent in QuadraWealth follows the **ReAct (Reasoning + Acting)** paradigm. This is the core "intelligence" of the system.

> [!NOTE]
> **Example Process: Market Research Agent Analyzing "NVDA"**
>
> 1. **THINK:** *"The user wants to analyze NVDA. I need its current price, basic fundamentals, and recent news sentiment to give a full picture."*
> 2. **ACT:** Calls `get_stock_quote(ticker="NVDA")` and `search_financial_news(query="NVDA")`.
> 3. **OBSERVE:** Receives JSON data: `{price: 900, pe: 75, sentiment: bullish}`.
> 4. **REASON:** *"While the P/E is high, the news sentiment is overwhelmingly bullish due to AI demand. I will recommend a 'Buy' but flag valuation risk."*
> 5. **ANSWER:** Writes the final report to the Orchestrator.

---

## 🏛️ System Components

| Component | Tech Stack | Role |
|-----------|------------|------|
| **Agent Modeling** | **Autonomous ReAct Coordination** | Multi-agent reasoning, planning, and synthesis. |
| **Tool Calling** | OpenAI Functions | Maps natural language intent to real Python service calls. |
| **Vector DB** | ChromaDB (RAG) | Stores and retrieves financial news for grounded analysis. |
| **Backend** | FastAPI | High-performance async API orchestrating the agents. |
| **Frontend** | Streamlit | Premium, dark-themed dashboard with "Reasoning Expanded" views. |
| **Data Sources** | yfinance / The Odds API | Real-time streams for stocks, sports, and macro data. |

---

## 📽️ Presentation Guide (For Teammate)

Use these points to build your slides for the final presentation:

### Slide 1: Motivation & Problem
- **Problem:** Financial data is fragmented (stocks, real estate, macro, betting). Manual synthesis is error-prone and slow.
- **Solution:** A multi-agent "Digital Twin" of a financial advisor that can autonomously research and synthesize any capital request.

### Slide 2: Technical Innovation (The "WOW" Factor)
- **Autonomous Tool Calling:** We didn't hard-code logic; we gave agents "tools" (APIs) and let the LLM decide when to use them.
- **Multi-Agent Collaboration:** The Orchestrator manages a team of specialists who share a "Shared Memory" scratchpad.
- **ReAct Pattern:** Demonstration of the "Think -> Act -> Observe" cycle for transparency.

### Slide 3: The Architecture
- Diagram: User -> Orchestrator -> [Market Agent, Risk Agent, etc.] -> [Tools/APIs].
- Explain how RAG (ChromaDB) ensures the agents aren't hallucinating news headlines.

### Slide 4: Real-World Use Cases
- "Hedge my stock portfolio with real estate." (Market + Real Estate agents collab).
- "Find me the best risk-free yield today." (Risk + Edge agents collab for arb vs bonds).

### Slide 5: Evaluation & Performance
- Explain how `gpt-4o-mini` allows for sub-10s synthesis of multi-source data.
- Mention the fallback "Template Mode" for reliability when API keys are missing.

---

## 🏆 Grading Highlights
- **Multi-Agent Collaboration?** ✅ Yes, Orchestrator delegates to 4 specialists.
- **LLM Integration?** ✅ Yes, full OpenAI GPT-4o-mini integration.
- **Tool Calling?** ✅ Yes, agents call yfinance, realestate, and betting services.
- **RAG?** ✅ Yes, searches ChromaDB for current news sentiment.
- **Complex Problem?** ✅ Yes, cross-asset capital optimization.
- **UI/API?** ✅ Yes, FastAPI docs and Streamlit dashboard.

---

Built for **CIS 4930 — Introduction to Agentic AI**.
