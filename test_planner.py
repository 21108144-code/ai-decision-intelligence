"""
Quick test script to verify the planner agent can be imported and executed.
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from dotenv import load_dotenv
load_dotenv()

async def test_planner():
    try:
        print("DEBUG: Importing planner_agent...")
        from app.agents.planner_agent import planner_agent
        from app.graph.state import AgentState
        
        print("DEBUG: Creating test state...")
        test_state = {
            "user_query": "What are the risks of a 4-day work week?",
            "messages": [],
            "execution_path": [],
            "agent_reasoning": {}
        }
        
        print("DEBUG: Calling planner_agent...")
        result = await planner_agent(test_state)
        
        print(f"DEBUG: Success! Execution plan created.")
        print(f"Plan preview: {result.get('execution_plan', 'N/A')[:200]}...")
        return True
        
    except Exception as e:
        print(f"ERROR: Planner agent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_planner())
    sys.exit(0 if success else 1)
