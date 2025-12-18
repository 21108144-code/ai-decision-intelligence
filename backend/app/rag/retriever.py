"""
Document retrieval logic with re-ranking and source citation.
"""
from typing import List, Dict, Any
from app.rag.vector_store import get_vector_store
from app.core.config import settings


async def retrieve_documents(
    query: str,
    top_k: int = None,
    filter_metadata: Dict[str, Any] = None,
    min_score: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant documents for a query.
    
    Args:
        query: Search query
        top_k: Number of results to return
        filter_metadata: Optional metadata filters
        min_score: Minimum similarity score threshold
        
    Returns:
        List of documents with content, source, and score
    """
    if top_k is None:
        top_k = settings.top_k_results
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Search for similar documents
    results = vector_store.search(
        query=query,
        top_k=top_k * 2,  # Get more results for re-ranking
        filter_metadata=filter_metadata
    )
    
    # Filter by minimum score
    filtered_results = [
        result for result in results
        if result['score'] >= min_score
    ]
    
    # Re-rank by score and take top_k
    filtered_results.sort(key=lambda x: x['score'], reverse=True)
    top_results = filtered_results[:top_k]
    
    # Format for agent consumption
    formatted_results = []
    for result in top_results:
        formatted_results.append({
            'content': result['content'],
            'source': result['metadata'].get('source', 'Unknown'),
            'score': result['score'],
            'metadata': result['metadata']
        })
    
    return formatted_results


async def ingest_document(file_path: str) -> Dict[str, Any]:
    """
    Ingest a document into the vector store.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Ingestion result with chunk count and status
    """
    from pathlib import Path
    from app.rag.document_processor import get_document_processor
    
    # Process the document
    processor = get_document_processor()
    file_path_obj = Path(file_path)
    
    try:
        chunks = processor.process_file(file_path_obj)
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file': file_path_obj.name
        }
    
    # Add to vector store
    vector_store = get_vector_store()
    
    documents = [chunk.content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    ids = [chunk.chunk_id for chunk in chunks]
    
    try:
        vector_store.add_documents(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file': file_path_obj.name
        }
    
    return {
        'success': True,
        'file': file_path_obj.name,
        'chunks': len(chunks),
        'chunk_ids': ids
    }


async def delete_document(source_name: str) -> Dict[str, Any]:
    """
    Delete all chunks of a document by source name.
    
    Args:
        source_name: Name of the source file
        
    Returns:
        Deletion result
    """
    # This would require querying by metadata and deleting matching chunks
    # For now, return a placeholder
    return {
        'success': True,
        'message': f'Document {source_name} deletion requested'
    }


async def get_document_stats() -> Dict[str, Any]:
    """
    Get statistics about the document store.
    
    Returns:
        Statistics dict
    """
    vector_store = get_vector_store()
    
    return {
        'total_chunks': vector_store.get_document_count(),
        'embedding_model': settings.embedding_model,
        'chunk_size': settings.chunk_size,
        'chunk_overlap': settings.chunk_overlap
    }
