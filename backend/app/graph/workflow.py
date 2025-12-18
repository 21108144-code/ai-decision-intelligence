"""
LangGraph workflow definition - connects all agents with conditional edges.
Implements the complete decision intelligence workflow with error recovery and human-in-the-loop.
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.graph.state import AgentState
from app.agents import (
    planner_agent,
    research_agent,
    validator_agent,
    risk_agent,
    decision_agent
)


def should_continue_research(state: AgentState) -> Literal["research", "risk"]:
    """
    Conditional edge: Determine if more research is needed after validation.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute
    """
    # Check if validator identified need for more research
    if state.get("needs_more_research", False):
        # Check iteration count to prevent infinite loops
        iteration = state.get("iteration_count", 0)
        if iteration < 2:  # Allow up to 2 research iterations
            return "research"
    
    # Proceed to risk assessment
    return "risk"


def should_wait_for_approval(state: AgentState) -> Literal["decision", "human_approval"]:
    """
    Conditional edge: Determine if human approval is needed before final decision.
    
    Args:
        state: Current agent state
        
    Returns:
        Next node to execute
    """
    # Check if risk agent flagged need for human approval
    if state.get("requires_human_approval", False):
        return "human_approval"
    
    # Proceed directly to decision
    return "decision"


def increment_iteration(state: AgentState) -> AgentState:
    """Helper to increment iteration count."""
    return {
        **state,
        "iteration_count": state.get("iteration_count", 0) + 1
    }


def build_workflow() -> StateGraph:
    """
    Build the complete LangGraph workflow.
    
    Returns:
        Compiled StateGraph
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("planner", planner_agent)
    workflow.add_node("research", research_agent)
    workflow.add_node("validator", validator_agent)
    workflow.add_node("risk", risk_agent)
    workflow.add_node("decision", decision_agent)
    
    # Add a node for iteration tracking
    workflow.add_node("increment_iteration", increment_iteration)
    
    # Define the workflow edges
    
    # Start with planner
    workflow.set_entry_point("planner")
    
    # Planner -> Research
    workflow.add_edge("planner", "research")
    
    # Research -> Validator
    workflow.add_edge("research", "validator")
    
    # Validator -> Conditional (more research OR risk assessment)
    workflow.add_conditional_edges(
        "validator",
        should_continue_research,
        {
            "research": "increment_iteration",  # Go through iteration counter
            "risk": "risk"
        }
    )
    
    # Increment iteration -> Research (for validation loop)
    workflow.add_edge("increment_iteration", "research")
    
    # Risk -> Conditional (human approval OR decision)
    workflow.add_conditional_edges(
        "risk",
        should_wait_for_approval,
        {
            "human_approval": "human_approval",
            "decision": "decision"
        }
    )
    
    # Human approval is an interrupt point - after approval, go to decision
    workflow.add_node("human_approval", lambda state: state)  # Pass-through node
    workflow.add_edge("human_approval", "decision")
    
    # Decision -> END
    workflow.add_edge("decision", END)
    
    return workflow


def create_graph():
    """
    Create and compile the workflow graph with memory.
    
    Returns:
        Compiled graph ready for execution
    """
    workflow = build_workflow()
    
    # Add memory for checkpointing (enables human-in-the-loop)
    memory = MemorySaver()
    
    # Compile the graph
    graph = workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_approval"]  # Interrupt before human approval
    )
    
    return graph


# Create the graph instance
decision_graph = create_graph()
