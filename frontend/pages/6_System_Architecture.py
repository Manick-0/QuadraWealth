import streamlit as st
import os

st.set_page_config(
    page_title="System Architecture — QuadraWealth",
    page_icon="🏛️",
    layout="wide",
)

# ── Custom CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

.main .block-container { padding-top: 2rem; max-width: 1200px; }

/* 🏛️ Architecture Section */
.arch-card {
    background: #1A1F2E;
    border-radius: 20px;
    padding: 2.5rem;
    border: 1px solid rgba(0, 212, 170, 0.15);
    margin-bottom: 2rem;
}

.tech-tag {
    display: inline-block;
    background: rgba(0, 212, 170, 0.1);
    color: #00D4AA;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 12px;
    margin-right: 8px;
    margin-bottom: 8px;
    border: 1px solid rgba(0, 212, 170, 0.2);
}

.compliance-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}
.compliance-table th, .compliance-table td {
    text-align: left;
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.compliance-table th { color: #00D4AA; text-transform: uppercase; font-size: 0.8rem; }

.status-check { color: #00D4AA; font-weight: 800; }

.logic-box {
    background: rgba(0,0,0,0.2);
    border-left: 4px solid #00D4AA;
    padding: 1.5rem;
    border-radius: 0 12px 12px 0;
    font-family: 'Inter', monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ── Top Hero ──
st.title("🏛️ Project Architecture & Technical Deep Dive")
st.markdown("#### QuadraWealth Case Study: Autonomous Multi-Agent Systems (CIS 4930)")
st.markdown("---")

cols = st.columns([2, 1])

with cols[0]:
    st.markdown("""
    ### 1. The Autonomous Multi-Agent Hierarchy
    QuadraWealth is built on a **Specialist-Orchestrator Architecture**. Unlike single-prompt AI, our system operates as a recursive network of decentralized experts coordinated by a central "Executive Brain."
    
    - **🏢 The Orchestrator (The Planner):** Uses high-level reasoning to decompose natural language queries into specific sub-tasks. It dispatches these tasks to the specialist network and performs a final synthesis.
    - **🛰️ Specialist Agents:** Each agent (Market, Risk, Edge, Real Estate) is a standalone "digital worker" with its own specific persona, tools, and memory context.
    """)

with cols[1]:
    st.markdown('<div class="arch-card">', unsafe_allow_html=True)
    st.markdown("#### Technical Stack")
    st.markdown("""
    <span class="tech-tag">FastAPI</span>
    <span class="tech-tag">Streamlit</span>
    <span class="tech-tag">OpenAI Function Calling</span>
    <span class="tech-tag">ChromaDB Vector Store</span>
    <span class="tech-tag">yfinance API</span>
    <span class="tech-tag">The Odds API</span>
    <span class="tech-tag">Pydantic</span>
    <span class="tech-tag">Asyncio</span>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ── ReAct Loop Explained ──
st.subheader("2. Inside the 'Reasoning Loop' (ReAct)")
st.write("Every specialist agent in QuadraWealth follows the **ReAct (Reason + Act)** pattern. This ensures the AI doesn't just 'guess'—it thinks, acts, and verifies.")

st.markdown("""
<div class="logic-box">
<b>STEP 1: THINK</b> — Agent reasons about the user's task and identifies missing information.<br>
<b>STEP 2: ACT</b> — Agent calls an external <b>Tool</b> (e.g., Stock Quote or News Search) via JSON-based function calling.<br>
<b>STEP 3: OBSERVE</b> — Agent receives the raw data result from the real world.<br>
<b>STEP 4: REASON</b> — Agent updates its understanding and decides if further tools are needed or if it can answer.<br>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── RAG and Tools ──
t_cols = st.columns(2)
with t_cols[0]:
    st.markdown("""
    ### 📖 RAG (Retrieval Augmented Generation)
    To prevent hallucinations, the **Market Research Agent** utilizes a **ChromaDB Vector Store**.
    1. **Ingest:** Recent financial news is embedded using OpenAI's embeddings.
    2. **Query:** When asked about a stock, the agent performs a semantic search.
    3. **Grounding:** The agent is forced to use the retrieved snippets to back up its multi-agent report.
    """)

with t_cols[1]:
    st.markdown("""
    ### 🛠️ External Tool Integration
    Our agents are empowered with 12+ real-world tools:
    - **Stocks:** Real-time yfinance quotes and historical technicals.
    - **Macro:** GDP, Inflation, and Fed Funds Rate via specialized scrapers.
    - **Real Estate:** Property investment analysis via Realty Mole (Mock Fallback).
    - **Betting:** Arbitrage and +EV detection via The Odds API.
    """)

st.markdown("---")

# ── SYLLABUS COMPLIANCE ──
st.subheader("🎓 Course Requirements & Compliance Matrix")
st.markdown("The following table demonstrates how this implementation meets and exceeds the **CIS 4930** final project requirements.")

st.markdown("""
<table class="compliance-table">
    <thead>
        <tr>
            <th>Requirement</th>
            <th>Implementation in QuadraWealth</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Multi-Agent Collaboration</td>
            <td>Orchestrator delegates core tasks to 4 specialists who share a central "Shared Memory" scratchpad.</td>
            <td class="status-check">✓ COMPLETE</td>
        </tr>
        <tr>
            <td>LLM Reasoning / ReAct</td>
            <td>Full implementation of the Think-Act-Observe cycle in <code>backend/agents/base.py</code>.</td>
            <td class="status-check">✓ COMPLETE</td>
        </tr>
        <tr>
            <td>Tool / Function Calling</td>
            <td>Native OpenAI Function Calling used to interface with yfinance, Odds-API, and internal calculators.</td>
            <td class="status-check">✓ COMPLETE</td>
        </tr>
        <tr>
            <td>Memory Management</td>
            <td>Persistent <code>AgentMemory</code> for chat context + <code>SharedMemory</code> for cross-agent data sharing.</td>
            <td class="status-check">✓ COMPLETE</td>
        </tr>
        <tr>
            <td>RAG Integration</td>
            <td>ChromaDB integration for news sentiment grounding in the Market Research specialist.</td>
            <td class="status-check">✓ COMPLETE</td>
        </tr>
        <tr>
            <td>System Planning</td>
            <td>Orchestrator generates a structured JSON execution plan before any specialists are activated.</td>
            <td class="status-check">✓ COMPLETE</td>
        </tr>
        <tr>
            <td>UI / Dashboard</td>
            <td>Modern Multi-page Streamlit Dashboard with Apple-style Chat UI and reasoning visualization.</td>
            <td class="status-check">✓ COMPLETE</td>
        </tr>
    </tbody>
</table>
""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Built as a final project for CIS 4930 — Introduction to Agentic AI | Professor: Guangjing Wang")
