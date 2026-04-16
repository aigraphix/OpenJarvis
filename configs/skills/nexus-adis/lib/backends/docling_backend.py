"""
NEXUS-ADIS Docling Backend
Advanced document parsing using IBM Docling

This backend handles complex documents:
- PDF with layout detection, tables, formulas
- DOCX, PPTX, XLSX
- OCR for scanned documents
- Audio transcription (ASR)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json

# Docling is optional - graceful degradation
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    DocumentConverter = None


class DoclingBackend:
    """
    High-fidelity document parser using IBM Docling.
    Falls back gracefully if Docling is not installed.
    """
    
    SUPPORTED_EXTENSIONS = {
        ".pdf", ".docx", ".pptx", ".xlsx",
        ".html", ".htm", ".png", ".jpg", 
        ".jpeg", ".tiff", ".wav", ".mp3"
    }
    
    def __init__(self):
        self.converter = None
        if DOCLING_AVAILABLE:
            self.converter = DocumentConverter()
    
    @property
    def available(self) -> bool:
        """Check if Docling is available."""
        return DOCLING_AVAILABLE and self.converter is not None
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if this backend can handle the file type."""
        if not self.available:
            return False
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a document using Docling.
        
        Returns:
            Dict with:
            - success: bool
            - content: str (extracted text)
            - elements: List[Dict] (structured elements)
            - metadata: Dict (document metadata)
            - format: str (output format used)
        """
        if not self.available:
            return {
                "success": False,
                "error": "Docling not installed. Run: pip install docling",
                "content": "",
                "elements": [],
                "metadata": {}
            }
        
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "content": "",
                "elements": [],
                "metadata": {}
            }
        
        try:
            # Convert document
            result = self.converter.convert(str(file_path))
            
            # Extract markdown content
            markdown_content = result.document.export_to_markdown()
            
            # Extract structured elements
            elements = self._extract_elements(result)
            
            # Build metadata
            metadata = {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "parser": "docling",
                "page_count": getattr(result.document, "num_pages", 1)
            }
            
            return {
                "success": True,
                "content": markdown_content,
                "elements": elements,
                "metadata": metadata,
                "format": "markdown"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "elements": [],
                "metadata": {"source": str(file_path)}
            }
    
    def _extract_elements(self, result) -> List[Dict[str, Any]]:
        """Extract structured elements from Docling result."""
        elements = []
        
        try:
            doc = result.document
            
            # Extract based on available attributes
            if hasattr(doc, "texts"):
                for i, text in enumerate(doc.texts):
                    elements.append({
                        "type": "text",
                        "index": i,
                        "content": str(text)[:500],  # Truncate for storage
                        "page": getattr(text, "page", None)
                    })
            
            if hasattr(doc, "tables"):
                for i, table in enumerate(doc.tables):
                    elements.append({
                        "type": "table",
                        "index": i,
                        "rows": getattr(table, "num_rows", 0),
                        "cols": getattr(table, "num_cols", 0),
                        "page": getattr(table, "page", None)
                    })
            
            if hasattr(doc, "pictures"):
                for i, pic in enumerate(doc.pictures):
                    elements.append({
                        "type": "figure",
                        "index": i,
                        "caption": getattr(pic, "caption", ""),
                        "page": getattr(pic, "page", None)
                    })
                    
        except Exception:
            pass  # Return whatever elements we got
        
        return elements
    
    def to_json(self, file_path: Path) -> str:
        """Parse and return JSON-serializable result."""
        result = self.parse(file_path)
        return json.dumps(result, indent=2, default=str)


# Singleton instance
_backend = None

def get_docling_backend() -> DoclingBackend:
    """Get or create the Docling backend singleton."""
    global _backend
    if _backend is None:
        _backend = DoclingBackend()
    return _backend
