"""
Analytics and monitoring API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.db.models import Conversation, Decision, Document as DocumentModel
from app.models import AnalyticsResponse
from app.rag import get_document_stats

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/metrics", response_model=AnalyticsResponse)
async def get_analytics_metrics(db: Session = Depends(get_db)):
    """Get system analytics and metrics."""
    
    # Count totals
    total_conversations = db.query(func.count(Conversation.id)).scalar()
    total_decisions = db.query(func.count(Decision.id)).scalar()
    total_documents = db.query(func.count(DocumentModel.id)).scalar()
    
    # Get averages
    avg_confidence = db.query(func.avg(Decision.confidence_score)).filter(
        Decision.confidence_score.isnot(None)
    ).scalar()
    
    avg_risk = db.query(func.avg(Decision.risk_score)).filter(
        Decision.risk_score.isnot(None)
    ).scalar()
    
    # Get vector store stats
    doc_stats = await get_document_stats()
    total_chunks = doc_stats.get('total_chunks', 0)
    
    return AnalyticsResponse(
        total_conversations=total_conversations or 0,
        total_decisions=total_decisions or 0,
        total_documents=total_documents or 0,
        total_chunks=total_chunks,
        avg_confidence_score=float(avg_confidence) if avg_confidence else None,
        avg_risk_score=float(avg_risk) if avg_risk else None
    )


@router.get("/decisions/recent")
async def get_recent_decisions(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent decisions with details."""
    decisions = db.query(Decision).order_by(
        Decision.started_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "execution_id": dec.execution_id,
            "query": dec.user_query,
            "status": dec.status,
            "confidence_score": dec.confidence_score,
            "risk_level": dec.risk_level,
            "started_at": dec.started_at.isoformat() if dec.started_at else None
        }
        for dec in decisions
    ]
