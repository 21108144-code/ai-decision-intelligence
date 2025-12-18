"""RAG package initialization."""
from app.rag.vector_store import get_vector_store, VectorStore
from app.rag.document_processor import get_document_processor, DocumentProcessor
from app.rag.retriever import retrieve_documents, ingest_document, get_document_stats

__all__ = [
    "get_vector_store",
    "VectorStore",
    "get_document_processor",
    "DocumentProcessor",
    "retrieve_documents",
    "ingest_document",
    "get_document_stats"
]
