from __future__ import annotations
"""
QuadraWealth Multi-Agent Orchestrator
Coordinates multiple specialist agents to solve complex financial queries.
Implements:
  1. Planning — Decomposing query into tasks for specialists
  2. Delegation — Dispatching tasks to specialist agents
  3. Synthesis — Combining all agent findings into a final master response
"""
import asyncio
import json
import logging
from typing import Optional

from backend.agents.llm import LLMClient
from backend.agents.memory import SharedMemory
from backend.agents.market_agent import create_market_agent
from backend.agents.risk_agent import create_risk_agent
from backend.agents.edge_agent import create_edge_agent
from backend.agents.realestate_agent import create_realestate_agent

logger = logging.getLogger("agents.orchestrator")


class Orchestrator:
    """
    The "Brain" of the QuadraWealth Agent System.
    Manages the lifecycle of a multi-agent request.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = LLMClient(model=model)
        self.shared_memory = SharedMemory()

        # Initialize specialist agents
        self.agents = {
            "market": create_market_agent(self.llm, self.shared_memory),
            "risk": create_risk_agent(self.llm, self.shared_memory),
            "edge": create_edge_agent(self.llm, self.shared_memory),
            "realestate": create_realestate_agent(self.llm, self.shared_memory),
        }

    async def chat(self, user_query: str, risk_tolerance: str = "moderate") -> dict:
        """Main entry point for multi-agent chat."""
        logger.info("🧠 Orchestrator received query: %s", user_query[:100])
        self.shared_memory.add_conversation_turn("user", user_query, agent="user")

        # 1. PLANNING — Determine which agents are needed
        plan = await self._create_plan(user_query)
        logger.info("📋 Execution Plan: %s", plan.get("needed_agents", []))

        # 2. DELEGATION — Run agents concurrently with a global timeout
        agent_tasks = []
        for agent_id, task_desc in plan.get("agent_tasks", {}).items():
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                # Pass context from risk tolerance
                context = f"User Risk Tolerance: {risk_tolerance}"
                agent_tasks.append(agent.process(task_desc, context=context))

        if agent_tasks:
            try:
                # Wrap the entire delegation in a 45s timeout
                agent_results = await asyncio.wait_for(
                    asyncio.gather(*agent_tasks),
                    timeout=45.0
                )
            except asyncio.TimeoutError:
                logger.error("Orchestrator timed out waiting for specialists")
                agent_results = []
        else:
            # Fallback if no specific agent was selected
            agent_results = []
            logger.warning("No specialists selected for this query.")

        # 3. SYNTHESIS — Combine findings into a final response
        final_response = await self._synthesize_final_answer(user_query, agent_results)

        # Return results to UI
        return {
            "query": user_query,
            "response": final_response,
            "agents_involved": plan.get("needed_agents", []),
            "agent_details": agent_results,
            "plan": plan,
        }

    async def _create_plan(self, query: str) -> dict:
        """Decompose the user query into a multi-agent execution plan."""
        system_prompt = """You are the QuadraWealth Orchestrator.
Your goal is to decompose a user's financial query into tasks for specialized agents.

Available Agents:
- market: Researches stocks, news, and market data. Use for stock picks, ticker info, and market sentiment.
- risk: Analyzes macro indicators, yield allocations (HYSA, Bonds), and overall portfolio risk.
- edge: Finds sports betting arbitrage and +EV opportunities.
- realestate: Screens and analyzes investment properties (real estate).

Output JSON only:
{
  "needed_agents": ["agent_id1", "agent_id2"],
  "agent_tasks": {
    "agent_id1": "specific task description",
    "agent_id2": "specific task description"
  },
  "rationale": "why these agents were chosen"
}
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        result = await self.llm.chat(messages=messages)
        content = result.get("content", "{}")

        try:
            # Handle markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            return json.loads(content)
        except Exception as e:
            logger.error("Failed to parse plan: %s | Content: %s", e, content)
            
            # Smart fallback plan based on keywords
            q_lower = query.lower()
            needed = []
            tasks = {}
            
            if any(k in q_lower for k in ["stock", "tesla", "apple", "nvidia", "aapl", "tsla", "market", "news"]):
                needed.append("market")
                tasks["market"] = f"Research market trends and metrics for: {query}"
            
            if any(k in q_lower for k in ["risk", "macro", "inflation", "gdp", "yield", "save", "bond", "portfolio"]):
                needed.append("risk")
                tasks["risk"] = f"Analyze macro-risk factors and yield allocation for: {query}"
                
            if any(k in q_lower for k in ["bet", "odds", "arb", "edge", "sports", "ev"]):
                needed.append("edge")
                tasks["edge"] = f"Check for betting edge or arbitrage in: {query}"
                
            if any(k in q_lower for k in ["property", "house", "real estate", "rent", "cap rate"]):
                needed.append("realestate")
                tasks["realestate"] = f"Analyze real estate investment metrics for: {query}"

            # Default if nothing matched
            if not needed:
                needed = ["market", "risk"]
                tasks = {
                    "market": f"Provide market perspective on: {query}",
                    "risk": f"Assess risk profile of: {query}"
                }

            return {
                "needed_agents": needed,
                "agent_tasks": tasks,
                "rationale": "Keyword-based fallback"
            }

    async def _synthesize_final_answer(self, query: str, agent_results: list[dict]) -> str:
        """Synthesize all specialist findings into a cohesive, persona-driven final response."""
        if not agent_results:
            return "I've analyzed your request. Based on current parameters, I recommend maintaining your current risk-adjusted position while we wait for more definitive market signals."

        # Compile findings
        findings_text = ""
        for res in agent_results:
            findings_text += f"\n\n### Findings from {res['agent']} ({res['role']}):\n{res['response']}"

        system_prompt = """You are the **QuadraWealth AI Advisor**, a prestigious multi-asset capital manager.
Your role is to synthesize specialized reports from your network of agents (Market, Risk, Edge, Real Estate) into a single, cohesive, and professional recommendation.

## Your Style
- Professional, authoritative, and data-driven
- Use formatting (markdown) effectively: headers, bold text, lists
- Synthesize conflicting information; don't just copy-paste
- Address the user directly and answer their specific "User Query"
- Provide a clear 'Executive Summary' and 'Final Verdict'
"""

        user_prompt = f"User Query: {query}\n\n Specialist Findings:\n{findings_text}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        result = await self.llm.chat(messages=messages)
        return result.get("content", "Synthesis failed. Please review the specialist reports below.")
