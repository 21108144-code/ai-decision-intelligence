"""
Research Agent - Performs RAG-based research and retrieves relevant information.
Integrates with the vector database to find and synthesize information.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.llm import get_llm
from app.graph.state import AgentState


RESEARCH_SYSTEM_PROMPT = """You are a research agent for an enterprise decision intelligence system.

Your role is to:
1. Retrieve relevant information from the knowledge base
2. Synthesize findings from multiple sources
3. Provide clear, well-sourced answers
4. Cite all sources accurately

Always:
- Base your answers on retrieved documents
- Cite sources with [Source: filename/URL]
- Acknowledge when information is not available
- Distinguish between facts and interpretations
- Highlight conflicting information if found

Be thorough, accurate, and objective."""


async def research_agent(state: AgentState) -> AgentState:
    """
    Research agent that retrieves and synthesizes information.
    SIMPLIFIED VERSION: Uses LLM knowledge directly instead of RAG.
    """
    llm = get_llm()
    
    # Get query and research areas
    query = state["user_query"]
    research_areas = state.get("required_research_areas", [])
    
    # Build research prompt (NO RAG - just use LLM knowledge)
    messages = [
        SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
        HumanMessage(content=f"""
User Query: {query}

Research Areas:
{chr(10).join(f"- {area}" for area in research_areas)}

Please provide comprehensive research findings that address the user's query and cover the identified research areas.
Use your knowledge to provide detailed, accurate information.
""")
    ]
    
    # Get LLM response
    response = await llm.ainvoke(messages)
    findings = response.content
    
    # Update state (no documents, no citations since we're not using RAG)
    return {
        **state,
        "research_findings": findings,
        "citations": ["LLM Knowledge Base"],
        "current_agent": "research",
        "agent_reasoning": {
            **state.get("agent_reasoning", {}),
            "research": findings
        },
        "execution_path": [*state.get("execution_path", []), "research"],
        "messages": [*state.get("messages", []), response]
    }
