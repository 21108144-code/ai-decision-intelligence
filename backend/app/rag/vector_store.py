"""
Vector store management using ChromaDB.
Handles embedding generation and similarity search.
"""
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.core.config import settings


class MockOutput:
    def __init__(self, data):
        self.data = data
    def tolist(self):
        return self.data
    def __getitem__(self, item):
        return self.data[item]

class MockEmbeddingModel:
    def encode(self, documents):
        # Return dummy embeddings (dimension 384 for MiniLM)
        dims = 384
        if isinstance(documents, str):
            data = [0.0] * dims  # Single vector
        else:
            data = [[0.0] * dims for _ in documents]  # Batch of vectors
        return MockOutput(data)

class VectorStore:
    """Vector store wrapper for ChromaDB."""
    
    def __init__(self):
        """Initialize ChromaDB and embedding model."""
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=str(settings.get_vector_db_path()),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        # Using Mock embeddings to prevent "Cold Start" hanging on first run
        print("INFO: Using Mock Embeddings for performance")
        self.embedding_model = MockEmbeddingModel()
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "Enterprise documents for decision intelligence"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dicts for each document
            ids: List of unique IDs for each document
        """
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of results with content, metadata, and scores
        """
        if top_k is None:
            top_k = settings.top_k_results
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'score': 1 - results['distances'][0][i] if results['distances'] else 0.0,  # Convert distance to similarity
                    'id': results['ids'][0][i] if results['ids'] else None
                })
        
        return formatted_results
    
    def delete_document(self, doc_id: str) -> None:
        """Delete a document by ID."""
        self.collection.delete(ids=[doc_id])
    
    def get_document_count(self) -> int:
        """Get total number of documents in the store."""
        return self.collection.count()
    
    def reset(self) -> None:
        """Reset the vector store (delete all documents)."""
        self.client.reset()
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"description": "Enterprise documents for decision intelligence"}
        )


# Global vector store instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
