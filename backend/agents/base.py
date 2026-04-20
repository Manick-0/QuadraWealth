from __future__ import annotations
"""
QuadraWealth Base Agent
Implements the ReAct (Reasoning + Acting) loop:
  Think → Act (tool call) → Observe → Repeat until answer.

All specialist agents inherit from this class.
"""
import asyncio
import json
import logging
from typing import Optional

from backend.agents.llm import LLMClient
from backend.agents.memory import AgentMemory, SharedMemory
from backend.agents.tools import Tool, get_tool_by_name

logger = logging.getLogger("agents.base")

# Maximum iterations for the ReAct loop to prevent infinite loops
MAX_REACT_STEPS = 5


class Agent:
    """
    Base AI Agent with ReAct reasoning loop and tool calling.

    Design pattern: ReAct (Reason + Act)
    1. THINK — LLM reasons about the current state
    2. ACT — LLM decides to call a tool or give a final answer
    3. OBSERVE — Agent executes the tool and feeds result back
    4. REPEAT — Until the agent has enough information to answer
    """

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        tools: list[Tool],
        llm: LLMClient,
        shared_memory: SharedMemory | None = None,
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.tools = tools
        self.llm = llm
        self.memory = AgentMemory()
        self.shared_memory = shared_memory or SharedMemory()

    async def process(self, task: str, context: str = "") -> dict:
        """
        Execute the ReAct loop for a given task.

        Returns:
            {
                "agent": str,
                "response": str,
                "tool_calls": list[dict],
                "reasoning_steps": list[str],
            }
        """
        logger.info("[%s] Processing task: %s", self.name, task[:100])

        # Build initial messages
        messages = [
            {"role": "system", "content": self._build_system_message(context)},
            {"role": "user", "content": task},
        ]

        tool_schemas = [t.to_openai_schema() for t in self.tools]
        tool_calls_log = []
        reasoning_steps = []
        final_response = ""

        # ── ReAct Loop ──
        for step in range(MAX_REACT_STEPS):
            logger.debug("[%s] ReAct step %d/%d", self.name, step + 1, MAX_REACT_STEPS)

            # THINK + ACT — Ask LLM what to do
            result = await self.llm.chat(
                messages=messages,
                tools=tool_schemas if self.tools else None,
            )

            content = result.get("content", "")
            tool_calls = result.get("tool_calls")

            if content:
                reasoning_steps.append(f"[Think] {content[:200]}")

            # If no tool calls, this is the final answer
            if not tool_calls:
                final_response = content
                reasoning_steps.append(f"[Answer] {content[:200]}")
                break

            # ACT — Execute tool calls
            # Add assistant message with tool calls to conversation
            assistant_msg = {"role": "assistant", "content": content or ""}
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"]),
                        },
                    }
                    for tc in tool_calls
                ]
            messages.append(assistant_msg)

            for tc in tool_calls:
                tool_name = tc["name"]
                tool_args = tc["arguments"]

                reasoning_steps.append(f"[Act] Calling tool: {tool_name}({json.dumps(tool_args)[:100]})")
                logger.info("[%s] Calling tool: %s", self.name, tool_name)

                # OBSERVE — Execute the tool with a timeout
                tool = get_tool_by_name(tool_name)
                if tool:
                    try:
                        # Tools are synchronous, so we run them in a thread or just hope they respond.
                        # Since most are I/O bound (yfinance), we use wait_for if they were async, 
                        # but these are sync. For now, we wrap the whole loop step in a timeout if possible,
                        # or just ensure tool.execute doesn't hang.
                        observation = await asyncio.wait_for(
                            asyncio.to_thread(tool.execute, **tool_args),
                            timeout=15.0
                        )
                    except asyncio.TimeoutError:
                        observation = json.dumps({"error": f"Tool {tool_name} timed out after 15s"})
                else:
                    observation = json.dumps({"error": f"Unknown tool: {tool_name}"})

                # Truncate large observations for context window
                if len(observation) > 3000:
                    observation = observation[:3000] + "\n... [truncated]"

                reasoning_steps.append(f"[Observe] {tool_name} returned {len(observation)} chars")

                # Record in memory
                self.memory.add_observation(tool_name, observation)
                tool_calls_log.append({
                    "tool": tool_name,
                    "args": tool_args,
                    "result_preview": observation[:300],
                })

                # Feed observation back into conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": observation,
                })

                # Write finding to shared memory
                self.shared_memory.write(
                    self.name,
                    f"tool:{tool_name}",
                    observation[:500],
                )

        # If we exhausted steps without a final answer, synthesize one
        if not final_response:
            final_response = await self._synthesize_from_observations()
            reasoning_steps.append(f"[Synthesize] Generated summary from {len(tool_calls_log)} tool calls")

        # Record in memory and shared memory
        self.memory.add_message("assistant", final_response)
        self.shared_memory.write(self.name, "final_answer", final_response[:1000])
        self.shared_memory.add_conversation_turn("assistant", final_response, agent=self.name)

        return {
            "agent": self.name,
            "role": self.role,
            "response": final_response,
            "tool_calls": tool_calls_log,
            "reasoning_steps": reasoning_steps,
        }

    def _build_system_message(self, context: str = "") -> str:
        """Build the full system message with role, context, and instructions."""
        parts = [
            self.system_prompt,
            "",
            "## Instructions",
            "- Use your available tools to gather data before making recommendations.",
            "- Think step-by-step. Reason about the data you receive.",
            "- Provide specific, actionable recommendations with concrete numbers.",
            "- If data is uncertain, acknowledge the uncertainty.",
            "- Cite the data sources (tool results) in your response.",
        ]

        if context:
            parts.extend(["", "## Context from Other Agents", context])

        # Add memory context
        mem_context = self.memory.get_context_summary()
        if mem_context != "No prior observations.":
            parts.extend(["", "## Prior Observations", mem_context])

        return "\n".join(parts)

    async def _synthesize_from_observations(self) -> str:
        """Generate a final response from all tool observations when ReAct loop completes."""
        observations = self.memory.get_recent_observations(5)
        if not observations:
            return "I was unable to gather sufficient data to provide a recommendation."

        obs_text = "\n".join([
            f"- {obs['tool']}: {obs['result'][:400]}"
            for obs in observations
        ])

        messages = [
            {
                "role": "system",
                "content": (
                    f"You are {self.name}, a {self.role}. "
                    f"Synthesize the following tool observations into a clear, "
                    f"actionable recommendation. Be specific with numbers and data."
                ),
            },
            {
                "role": "user",
                "content": f"Based on these observations, provide your analysis:\n\n{obs_text}",
            },
        ]

        result = await self.llm.chat(messages=messages)
        return result.get("content", "Analysis complete based on available data.")
