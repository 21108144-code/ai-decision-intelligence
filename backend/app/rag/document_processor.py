"""
Document processing and chunking for RAG pipeline.
Supports PDF, DOCX, TXT, CSV, and JSON files.
"""
from typing import List, Dict, Any
from pathlib import Path
import uuid
import json
import csv
from io import StringIO

# Document parsing libraries
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

from app.core.config import settings


class DocumentChunk:
    """Represents a chunk of a document."""
    
    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_id: str = None
    ):
        self.content = content
        self.metadata = metadata
        self.chunk_id = chunk_id or str(uuid.uuid4())


class DocumentProcessor:
    """Process and chunk documents for RAG."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def process_file(self, file_path: Path) -> List[DocumentChunk]:
        """
        Process a file and return document chunks.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of DocumentChunk objects
        """
        suffix = file_path.suffix.lower()
        
        # Extract text based on file type
        if suffix == '.pdf':
            text = self._extract_pdf(file_path)
        elif suffix in ['.docx', '.doc']:
            text = self._extract_docx(file_path)
        elif suffix == '.txt':
            text = self._extract_txt(file_path)
        elif suffix == '.csv':
            text = self._extract_csv(file_path)
        elif suffix == '.json':
            text = self._extract_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        # Create base metadata
        metadata = {
            'source': file_path.name,
            'file_type': suffix,
            'file_path': str(file_path)
        }
        
        # Chunk the text
        chunks = self._chunk_text(text, metadata)
        
        return chunks
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF."""
        if PdfReader is None:
            raise ImportError("pypdf is required for PDF processing")
        
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX."""
        if DocxDocument is None:
            raise ImportError("python-docx is required for DOCX processing")
        
        doc = DocxDocument(file_path)
        text = "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def _extract_txt(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _extract_csv(self, file_path: Path) -> str:
        """Extract text from CSV."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Convert to readable text format
            text = f"CSV Data with {len(rows)} rows:\n\n"
            for i, row in enumerate(rows[:100], 1):  # Limit to first 100 rows
                text += f"Row {i}:\n"
                for key, value in row.items():
                    text += f"  {key}: {value}\n"
                text += "\n"
            
            if len(rows) > 100:
                text += f"... and {len(rows) - 100} more rows"
            
            return text
    
    def _extract_json(self, file_path: Path) -> str:
        """Extract text from JSON."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Convert to readable text format
            return json.dumps(data, indent=2)
    
    def _chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:
        """
        Chunk text using recursive character splitting with overlap.
        
        Args:
            text: Text to chunk
            metadata: Base metadata for all chunks
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunk_metadata = {
                    **metadata,
                    'chunk_index': chunk_index,
                    'chunk_size': len(current_chunk)
                }
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    metadata=chunk_metadata
                ))
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                current_chunk = overlap_text + "\n\n" + paragraph
                chunk_index += 1
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add final chunk
        if current_chunk:
            chunk_metadata = {
                **metadata,
                'chunk_index': chunk_index,
                'chunk_size': len(current_chunk)
            }
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                metadata=chunk_metadata
            ))
        
        return chunks


# Global processor instance
_processor = None


def get_document_processor() -> DocumentProcessor:
    """Get or create the global document processor instance."""
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor
