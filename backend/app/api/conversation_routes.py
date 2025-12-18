"""
Conversation management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.db.models import Conversation, Message, Decision
from app.models import ConversationResponse, MessageResponse, DecisionResponse

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("/", response_model=list[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List all conversations."""
    conversations = db.query(Conversation).order_by(
        Conversation.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for conv in conversations:
        message_count = db.query(func.count(Message.id)).filter(
            Message.conversation_id == conv.id
        ).scalar()
        
        result.append(ConversationResponse(
            id=conv.id,
            session_id=conv.session_id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=message_count
        ))
    
    return result


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get conversation details."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message_count = db.query(func.count(Message.id)).filter(
        Message.conversation_id == conversation.id
    ).scalar()
    
    return ConversationResponse(
        id=conversation.id,
        session_id=conversation.session_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=message_count
    )


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    return [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at
        )
        for msg in messages
    ]


@router.get("/{conversation_id}/decisions", response_model=list[DecisionResponse])
async def get_conversation_decisions(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get all decisions in a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    decisions = db.query(Decision).filter(
        Decision.conversation_id == conversation_id
    ).order_by(Decision.started_at.desc()).all()
    
    return [
        DecisionResponse(
            id=dec.id,
            execution_id=dec.execution_id,
            user_query=dec.user_query,
            final_decision=dec.final_decision,
            confidence_score=dec.confidence_score,
            risk_score=dec.risk_score,
            risk_level=dec.risk_level,
            status=dec.status,
            requires_approval=dec.requires_approval,
            approved=dec.approved,
            started_at=dec.started_at,
            completed_at=dec.completed_at
        )
        for dec in decisions
    ]
