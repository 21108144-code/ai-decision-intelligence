"""
LangGraph state schema definition.
Defines the complete state structure for the multi-agent decision workflow.
"""
from typing import Annotated, TypedDict, Literal
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    State schema for the decision intelligence workflow.
    
    This state is passed between all agents and maintains the complete
    context of the decision-making process.
    """
    
    # Messages - conversation history with add_messages reducer
    messages: Annotated[list[BaseMessage], add_messages]
    
    # User Input
    user_query: str
    session_id: str
    
    # Planning
    execution_plan: str | None
    required_research_areas: list[str]
    
    # Research & RAG
    retrieved_documents: list[dict]  # {content, source, score}
    research_findings: str | None
    citations: list[str]
    
    # Validation
    validation_result: str | None
    validation_passed: bool
    identified_gaps: list[str]
    needs_more_research: bool
    
    # Risk Assessment
    risk_score: float  # 0.0 to 1.0
    risk_level: Literal["low", "medium", "high", "critical"] | None
    compliance_issues: list[str]
    risk_mitigation: list[str]
    
    # Decision
    final_decision: str | None
    confidence_score: float  # 0.0 to 1.0
    recommendations: list[str]
    alternative_options: list[str]
    
    # Metadata & Control Flow
    current_agent: str | None
    iteration_count: int
    requires_human_approval: bool
    human_feedback: str | None
    error_message: str | None
    
    # Audit Trail
    agent_reasoning: dict[str, str]  # {agent_name: reasoning}
    execution_path: list[str]  # Track which agents executed
    
    # Timestamps
    started_at: str | None
    completed_at: str | None


class GraphConfig(TypedDict):
    """Configuration for graph execution."""
    
    thread_id: str
    checkpoint_ns: str
    recursion_limit: int


def create_initial_state(
    user_query: str,
    session_id: str
) -> AgentState:
    """
    Create initial state for a new decision workflow.
    
    Args:
        user_query: The user's question or request
        session_id: Unique session identifier
        
    Returns:
        Initial AgentState
    """
    from datetime import datetime
    
    return AgentState(
        messages=[],
        user_query=user_query,
        session_id=session_id,
        execution_plan=None,
        required_research_areas=[],
        retrieved_documents=[],
        research_findings=None,
        citations=[],
        validation_result=None,
        validation_passed=False,
        identified_gaps=[],
        needs_more_research=False,
        risk_score=0.0,
        risk_level=None,
        compliance_issues=[],
        risk_mitigation=[],
        final_decision=None,
        confidence_score=0.0,
        recommendations=[],
        alternative_options=[],
        current_agent=None,
        iteration_count=0,
        requires_human_approval=False,
        human_feedback=None,
        error_message=None,
        agent_reasoning={},
        execution_path=[],
        started_at=datetime.utcnow().isoformat(),
        completed_at=None
    )
