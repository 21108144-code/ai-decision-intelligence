"""
Planner Agent - Analyzes user requests and creates execution plans.
First agent in the workflow that breaks down complex queries.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.logger import logger
from app.core.llm import get_llm
from app.graph.state import AgentState


PLANNER_SYSTEM_PROMPT = """You are a strategic planning agent for an enterprise decision intelligence system.

Your role is to:
1. Analyze the user's query and understand their decision-making needs
2. Break down complex questions into specific research areas
3. Create a structured execution plan
4. Identify what information is needed to make an informed decision

Consider:
- What business context is needed?
- What policies or regulations might apply?
- What risks should be assessed?
- What data or documents should be consulted?

Provide a clear, actionable plan that other agents can follow."""


async def planner_agent(state: AgentState) -> AgentState:
    """
    Planner agent that analyzes the query and creates an execution plan.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with execution plan and research areas
    """
    logger.info(f"Planner Agent started. Query: {state.get('user_query')}")
    llm = get_llm()
    
    # Build the planning prompt
    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"""
User Query: {state['user_query']}

Please analyze this query and provide:
1. A structured execution plan
2. Specific research areas that need investigation
3. Key questions that need to be answered

Format your response as:

EXECUTION PLAN:
[Your detailed plan]

RESEARCH AREAS:
- [Area 1]
- [Area 2]
- [Area 3]
...

KEY QUESTIONS:
- [Question 1]
- [Question 2]
...
""")
    ]
    
    # Get LLM response
    try:
        logger.info("Planner Agent calling LLM...")
        response = await llm.ainvoke(messages)
        logger.info("Planner Agent received response")
        plan_text = response.content
    except Exception as e:
        logger.error(f"Planner Agent FAILED: {str(e)}")
        # Return fallback state to prevent hang
        return {
            **state,
            "error": str(e),
            "execution_plan": "Error generating plan. Proceeding with default flow.",
            "required_research_areas": ["General Analysis", "Risk Assessment"],
            "current_agent": "planner"
        }
    
    # Parse research areas from the response
    research_areas = []
    if "RESEARCH AREAS:" in plan_text:
        areas_section = plan_text.split("RESEARCH AREAS:")[1]
        if "KEY QUESTIONS:" in areas_section:
            areas_section = areas_section.split("KEY QUESTIONS:")[0]
        
        for line in areas_section.strip().split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                research_areas.append(line.lstrip("-•").strip())
    
    # Update state
    return {
        **state,
        "execution_plan": plan_text,
        "required_research_areas": research_areas,
        "current_agent": "planner",
        "agent_reasoning": {
            **state.get("agent_reasoning", {}),
            "planner": plan_text
        },
        "execution_path": [*state.get("execution_path", []), "planner"],
        "messages": [*state.get("messages", []), response]
    }
