from __future__ import annotations
"""
QuadraWealth Agent Router
API endpoints for the multi-agent AI advisor.
"""
import logging
from fastapi import APIRouter, HTTPException

from backend.models.schemas import AgentChatRequest, AgentChatResponse
from backend.agents.orchestrator import Orchestrator

logger = logging.getLogger("routers.agents")
router = APIRouter()

# Singleton orchestrator (prevents reloading LLM config on every request)
_orchestrator = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


@router.post("/chat", response_model=AgentChatResponse)
async def chat_with_agents(request: AgentChatRequest):
    """
    Submit a query to the Multi-Agent Orchestrator.
    The orchestrator will plan, delegate to specialists, and synthesize a final answer.
    """
    try:
        orch = get_orchestrator()
        result = await orch.chat(
            user_query=request.query,
            risk_tolerance=request.risk_tolerance
        )

        # Map to response schema
        return AgentChatResponse(
            query=result["query"],
            response=result["response"],
            agents_involved=result["agents_involved"],
            agent_details=[
                {
                    "agent": d["agent"],
                    "role": d["role"],
                    "response": d["response"],
                    "reasoning_steps": d["reasoning_steps"]
                }
                for d in result["agent_details"]
            ],
            execution_plan=result["plan"]
        )

    except Exception as e:
        logger.error("Orchestrator error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_agent_status():
    """Check LLM connectivity and agent availability."""
    orch = get_orchestrator()
    return {
        "llm_live": orch.llm.is_live,
        "agents": list(orch.agents.keys()),
        "modeling": "Autonomous ReAct Multi-Agent Coordination"
    }
