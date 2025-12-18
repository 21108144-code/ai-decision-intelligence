"""
Database models using SQLAlchemy.
Supports both SQLite and PostgreSQL.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model (for future authentication)."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    """Conversation session model."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Chat message model."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    """Uploaded document model."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    
    # Metadata
    meta_data = Column(JSON, nullable=True)


class Decision(Base):
    """Decision record model."""
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Query
    user_query = Column(Text, nullable=False)
    
    # Results
    final_decision = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    requires_approval = Column(Boolean, default=False)
    approved = Column(Boolean, nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Full state (JSON)
    state_data = Column(JSON, nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="decisions")
    audit_logs = relationship("AuditLog", back_populates="decision", cascade="all, delete-orphan")


class AuditLog(Base):
    """Audit trail for decision-making process."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False)
    
    agent_name = Column(String(100), nullable=False)
    reasoning = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Additional data
    meta_data = Column(JSON, nullable=True)
    
    # Relationships
    decision = relationship("Decision", back_populates="audit_logs")


class Execution(Base):
    """Graph execution tracking."""
    __tablename__ = "executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)
    session_id = Column(String(100), index=True, nullable=False)
    
    status = Column(String(50), default="running")  # running, completed, failed, interrupted
    current_node = Column(String(100), nullable=True)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Full state snapshot
    state_snapshot = Column(JSON, nullable=True)
