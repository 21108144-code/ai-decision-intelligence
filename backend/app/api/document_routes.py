"""
Document management API endpoints.
Handles file upload, ingestion, and retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from datetime import datetime

from app.db import get_db
from app.db.models import Document as DocumentModel
from app.models import DocumentUploadResponse, DocumentResponse, IngestRequest
from app.core.config import settings
from app.rag import ingest_document, get_document_stats

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document file.
    
    Args:
        file: Uploaded file
        db: Database session
        
    Returns:
        Upload response with file details
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower().lstrip('.')
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {settings.allowed_extensions}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB"
        )
    
    # Save file
    upload_dir = settings.get_upload_dir()
    file_path = upload_dir / file.filename
    
    # Handle duplicate filenames
    counter = 1
    while file_path.exists():
        stem = Path(file.filename).stem
        file_path = upload_dir / f"{stem}_{counter}{Path(file.filename).suffix}"
        counter += 1
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create database record
    document = DocumentModel(
        filename=file_path.name,
        file_path=str(file_path),
        file_type=file_ext,
        file_size=file_size,
        processed=False
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return DocumentUploadResponse(
        success=True,
        filename=file_path.name,
        file_id=document.id,
        message="File uploaded successfully"
    )


@router.post("/ingest")
async def ingest_uploaded_document(
    request: IngestRequest,
    db: Session = Depends(get_db)
):
    """
    Ingest an uploaded document into the vector store.
    
    Args:
        request: Ingest request with file ID
        db: Database session
        
    Returns:
        Ingestion result
    """
    # Get document from database
    document = db.query(DocumentModel).filter(
        DocumentModel.id == request.file_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Ingest the document
    result = await ingest_document(document.file_path)
    
    if result['success']:
        # Update document record
        document.processed = True
        document.chunk_count = result['chunks']
        db.commit()
    
    return result


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all uploaded documents."""
    documents = db.query(DocumentModel).offset(skip).limit(limit).all()
    
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            uploaded_at=doc.uploaded_at,
            processed=doc.processed,
            chunk_count=doc.chunk_count
        )
        for doc in documents
    ]


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = db.query(DocumentModel).filter(
        DocumentModel.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from filesystem
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}


@router.get("/stats")
async def get_stats():
    """Get document store statistics."""
    stats = await get_document_stats()
    return stats
