"""
Pydantic models for API request/response validation.
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# Request Models

class ExecuteRequest(BaseModel):
    """Request to execute decision workflow."""
    query: str = Field(..., description="User's question or decision request")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ApprovalRequest(BaseModel):
    """Request to approve a decision."""
    approved: bool = Field(..., description="Whether the decision is approved")
    feedback: Optional[str] = Field(None, description="Optional feedback from human reviewer")


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    success: bool
    filename: str
    file_id: Optional[int] = None
    message: str


class IngestRequest(BaseModel):
    """Request to ingest a document."""
    file_id: int = Field(..., description="ID of the uploaded file")


# Response Models

class AgentReasoningResponse(BaseModel):
    """Agent reasoning in the workflow."""
    agent_name: str
    reasoning: str


class ExecutionResponse(BaseModel):
    """Response from workflow execution."""
    execution_id: str
    session_id: str
    status: Literal["running", "completed", "failed", "awaiting_approval"]
    
    # Results (if completed)
    final_decision: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    recommendations: List[str] = []
    alternative_options: List[str] = []
    citations: List[str] = []
    
    # Audit trail
    agent_reasoning: Dict[str, str] = {}
    execution_path: List[str] = []
    
    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Error
    error_message: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation details."""
    id: int
    session_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class MessageResponse(BaseModel):
    """Message details."""
    id: int
    role: str
    content: str
    created_at: datetime


class DecisionResponse(BaseModel):
    """Decision record details."""
    id: int
    execution_id: str
    user_query: str
    final_decision: Optional[str]
    confidence_score: Optional[float]
    risk_score: Optional[float]
    risk_level: Optional[str]
    status: str
    requires_approval: bool
    approved: Optional[bool]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class DocumentResponse(BaseModel):
    """Document details."""
    id: int
    filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    processed: bool
    chunk_count: int


class AnalyticsResponse(BaseModel):
    """System analytics."""
    total_conversations: int
    total_decisions: int
    total_documents: int
    total_chunks: int
    avg_confidence_score: Optional[float]
    avg_risk_score: Optional[float]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    llm_provider: str
    database: str
    vector_store_chunks: int
