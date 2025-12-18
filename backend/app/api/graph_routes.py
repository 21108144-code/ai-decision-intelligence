"""
Graph execution API endpoints.
Handles workflow execution, streaming, and human approval.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import AsyncGenerator
import uuid
import json
from datetime import datetime

from app.db import get_db
from app.db.models import Conversation, Decision, AuditLog, Execution
from app.models import ExecuteRequest, ExecutionResponse, ApprovalRequest
from app.graph import create_initial_state, decision_graph
from app.core.logger import logger

router = APIRouter(prefix="/api", tags=["graph"])


@router.post("/execute", response_model=ExecutionResponse)
async def execute_workflow(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Execute the decision intelligence workflow.
    
    Args:
        request: Execution request with query and optional session_id
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Execution response with results
    """
    # Generate IDs
    session_id = request.session_id or str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    
    # Get or create conversation
    conversation = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).first()
    
    if not conversation:
        conversation = Conversation(
            session_id=session_id,
            title=request.query[:100]  # Use first 100 chars as title
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Create decision record
    decision = Decision(
        conversation_id=conversation.id,
        execution_id=execution_id,
        user_query=request.query,
        status="running",
        started_at=datetime.utcnow()
    )
    db.add(decision)
    db.commit()
    
    # Create initial state
    initial_state = create_initial_state(
        user_query=request.query,
        session_id=session_id
    )
    
    try:
        # Execute the graph
        config = {"configurable": {"thread_id": session_id}}
        accumulated_state = dict(initial_state)  # Start with initial state
        
        async for step_output in decision_graph.astream(initial_state, config):
            logger.info(f"Graph step completed. Keys: {list(step_output.keys()) if step_output else 'None'}")
            # Each step_output is {node_name: node_output_dict}
            # Merge node outputs into accumulated state
            for node_name, node_output in step_output.items():
                if isinstance(node_output, dict):
                    accumulated_state.update(node_output)
                    logger.info(f"Merged output from node: {node_name}")
        
        # Use the accumulated state
        state_dict = accumulated_state
        
        if state_dict and state_dict.get("execution_path"):
            # Update decision record
            decision.final_decision = state_dict.get("final_decision")
            decision.confidence_score = state_dict.get("confidence_score")
            decision.risk_score = state_dict.get("risk_score")
            decision.risk_level = state_dict.get("risk_level")
            decision.requires_approval = state_dict.get("requires_human_approval", False)
            decision.state_data = {k: v for k, v in state_dict.items() if k != "messages"}  # Exclude messages for JSON serialization
            decision.completed_at = datetime.utcnow()
            
            # Determine status
            if decision.requires_approval:
                decision.status = "awaiting_approval"
            else:
                decision.status = "completed"
            
            # Create audit logs
            agent_reasoning = state_dict.get("agent_reasoning", {})
            for agent_name, reasoning in agent_reasoning.items():
                audit_log = AuditLog(
                    decision_id=decision.id,
                    agent_name=agent_name,
                    reasoning=reasoning
                )
                db.add(audit_log)
            
            db.commit()
            
            # Build response
            return ExecutionResponse(
                execution_id=execution_id,
                session_id=session_id,
                status=decision.status,
                final_decision=state_dict.get("final_decision"),
                confidence_score=state_dict.get("confidence_score"),
                risk_score=state_dict.get("risk_score"),
                risk_level=state_dict.get("risk_level"),
                recommendations=state_dict.get("recommendations", []),
                alternative_options=state_dict.get("alternative_options", []),
                citations=state_dict.get("citations", []),
                agent_reasoning=state_dict.get("agent_reasoning", {}),
                execution_path=state_dict.get("execution_path", []),
                started_at=state_dict.get("started_at"),
                completed_at=state_dict.get("completed_at")
            )
        else:
            raise HTTPException(status_code=500, detail="Workflow execution failed")
            
    except Exception as e:
        decision.status = "failed"
        decision.completed_at = datetime.utcnow()
        db.commit()
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution/{execution_id}", response_model=ExecutionResponse)
async def get_execution_status(
    execution_id: str,
    db: Session = Depends(get_db)
):
    """Get execution status and results."""
    decision = db.query(Decision).filter(
        Decision.execution_id == execution_id
    ).first()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    state_data = decision.state_data or {}
    
    return ExecutionResponse(
        execution_id=decision.execution_id,
        session_id=decision.conversation.session_id,
        status=decision.status,
        final_decision=decision.final_decision,
        confidence_score=decision.confidence_score,
        risk_score=decision.risk_score,
        risk_level=decision.risk_level,
        recommendations=state_data.get("recommendations", []),
        alternative_options=state_data.get("alternative_options", []),
        citations=state_data.get("citations", []),
        agent_reasoning=state_data.get("agent_reasoning", {}),
        execution_path=state_data.get("execution_path", []),
        started_at=decision.started_at.isoformat() if decision.started_at else None,
        completed_at=decision.completed_at.isoformat() if decision.completed_at else None
    )


@router.post("/execution/{execution_id}/approve")
async def approve_decision(
    execution_id: str,
    request: ApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve or reject a decision requiring human review."""
    decision = db.query(Decision).filter(
        Decision.execution_id == execution_id
    ).first()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if not decision.requires_approval:
        raise HTTPException(status_code=400, detail="This decision does not require approval")
    
    decision.approved = request.approved
    decision.status = "completed" if request.approved else "rejected"
    
    # Store feedback in state data
    if request.feedback:
        state_data = decision.state_data or {}
        state_data["human_feedback"] = request.feedback
        decision.state_data = state_data
    
    db.commit()
    
    return {"message": "Decision updated", "approved": request.approved}
