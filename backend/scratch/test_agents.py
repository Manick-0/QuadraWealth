import asyncio
import sys
import os
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).parent.parent.parent
sys.path.append(str(root))

from backend.agents.orchestrator import Orchestrator

async def test_orchestrator():
    print("🚀 Initializing Multi-Agent Orchestrator...")
    orch = Orchestrator()
    
    query = "Search tech stocks and check for any news regarding Apple. Also tell me if there's any arbitrage edge today."
    print(f"\n💬 Query: {query}")
    
    print("\n🧠 Processing (Multi-Agent collaboration)...")
    result = await orch.chat(query)
    
    print("\n✅ Final Synthesis:")
    print("-" * 50)
    print(result["response"])
    print("-" * 50)
    
    print("\n🔍 Agents Involved:", result["agents_involved"])
    print("\n📋 Execution Plan:", result["plan"].get("rationale"))
    
    for detail in result["agent_details"]:
        print(f"\n🛰️ Agent: {detail['agent']} ({detail['role']})")
        print(f"   Reasoning steps: {len(detail['reasoning_steps'])}")
        print(f"   Response len: {len(detail['response'])}")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())
