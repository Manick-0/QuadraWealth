from __future__ import annotations
"""
QuadraWealth Agent Memory
Conversation history and shared scratchpad for multi-agent collaboration.
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger("agents.memory")


class AgentMemory:
    """
    Per-agent memory that stores conversation history and observations.
    Supports both short-term (current session) and context window management.
    """

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self._history: list[dict] = []
        self._observations: list[dict] = []

    def add_message(self, role: str, content: str, metadata: dict | None = None):
        """Add a message to conversation history."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self._history.append(entry)

        # Trim to max
        if len(self._history) > self.max_history:
            self._history = self._history[-self.max_history:]

    def add_observation(self, tool_name: str, result: str):
        """Record a tool observation (result of a tool call)."""
        self._observations.append({
            "tool": tool_name,
            "result": result[:2000],  # Cap for context window
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_messages_for_prompt(self) -> list[dict]:
        """Return history formatted for LLM messages."""
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self._history
        ]

    def get_recent_observations(self, n: int = 5) -> list[dict]:
        """Return the N most recent tool observations."""
        return self._observations[-n:]

    def get_context_summary(self) -> str:
        """Generate a compact context summary from memory."""
        parts = []
        if self._observations:
            parts.append("Recent tool results:")
            for obs in self._observations[-3:]:
                parts.append(f"  - {obs['tool']}: {obs['result'][:200]}...")
        return "\n".join(parts) if parts else "No prior observations."

    def clear(self):
        """Reset memory."""
        self._history.clear()
        self._observations.clear()


class SharedMemory:
    """
    Shared scratchpad for multi-agent collaboration.
    Agents write findings here; the orchestrator reads from all agents.
    """

    def __init__(self):
        self._scratchpad: dict[str, list[dict]] = {}
        self._conversation: list[dict] = []

    def write(self, agent_name: str, key: str, value: str):
        """An agent writes a finding to the shared scratchpad."""
        if agent_name not in self._scratchpad:
            self._scratchpad[agent_name] = []

        self._scratchpad[agent_name].append({
            "key": key,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
        })
        logger.debug("[SharedMemory] %s wrote '%s'", agent_name, key)

    def read(self, agent_name: str | None = None) -> dict:
        """
        Read the scratchpad.
        If agent_name is given, read only that agent's entries.
        Otherwise, read all.
        """
        if agent_name:
            return {agent_name: self._scratchpad.get(agent_name, [])}
        return dict(self._scratchpad)

    def read_all_findings(self) -> str:
        """Compile all agent findings into a readable summary."""
        parts = []
        for agent, entries in self._scratchpad.items():
            parts.append(f"\n=== {agent} ===")
            for entry in entries:
                parts.append(f"[{entry['key']}]: {entry['value']}")
        return "\n".join(parts) if parts else "No findings yet."

    def add_conversation_turn(self, role: str, content: str, agent: str = "system"):
        """Track the full multi-agent conversation."""
        self._conversation.append({
            "role": role,
            "content": content,
            "agent": agent,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_conversation(self) -> list[dict]:
        """Return the full conversation history."""
        return list(self._conversation)

    def clear(self):
        """Reset shared memory."""
        self._scratchpad.clear()
        self._conversation.clear()
