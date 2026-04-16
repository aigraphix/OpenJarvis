"""
NEXUS-ADIS Engine
Advanced Data Intelligence System - Unified Parser Engine

This is the main entry point for document parsing. It intelligently routes
documents to the best available backend (Docling or Native).
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import time

# Add skill lib to path
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))

from lib.backends.docling_backend import DoclingBackend, get_docling_backend
from lib.backends.native_backend import NativeBackend, get_native_backend


class ADISEngine:
    """
    NEXUS Advanced Data Intelligence System
    
    Unified parser engine that routes documents to the optimal backend
    based on file type and backend availability.
    """
    
    VERSION = "3.0"
    
    def __init__(self):
        self.docling = get_docling_backend()
        self.native = get_native_backend()
        self._parse_count = 0
        self._error_count = 0
    
    @property
    def docling_available(self) -> bool:
        """Check if Docling backend is available."""
        return self.docling.available
    
    def parse(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse any supported document format.
        
        Intelligently routes to the best backend:
        - Docling for complex formats (PDF, DOCX, PPTX)
        - Native for simple formats (MD, JSON, CSV)
        - Falls back to Native if Docling unavailable
        
        Args:
            file_path: Path to the document to parse
            
        Returns:
            Dict with:
            - success: bool
            - content: str (extracted text)
            - elements: List[Dict] (structured elements)
            - metadata: Dict (document metadata)
            - format: str (output format)
            - engine: str (which backend was used)
        """
        path = Path(file_path)
        start_time = time.time()
        
        if not path.exists():
            self._error_count += 1
            return {
                "success": False,
                "error": f"File not found: {path}",
                "content": "",
                "elements": [],
                "metadata": {},
                "engine": "none"
            }
        
        # Route to appropriate backend
        result = self._route_and_parse(path)
        
        # Add timing and engine info
        result["parse_time_ms"] = int((time.time() - start_time) * 1000)
        result["adis_version"] = self.VERSION
        
        if result["success"]:
            self._parse_count += 1
        else:
            self._error_count += 1
        
        return result
    
    def _route_and_parse(self, path: Path) -> Dict[str, Any]:
        """Route to the best backend and parse."""
        ext = path.suffix.lower()
        
        # Complex formats → prefer Docling
        complex_formats = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm"}
        
        # Simple formats → prefer Native (faster)
        simple_formats = {".txt", ".md", ".markdown", ".json", ".yaml", ".yml", ".csv", ".tsv"}
        
        # Media formats → Docling only
        media_formats = {".png", ".jpg", ".jpeg", ".tiff", ".wav", ".mp3"}
        
        if ext in simple_formats:
            # Use Native for simple formats (faster)
            result = self.native.parse(path)
            result["engine"] = "native"
            return result
        
        elif ext in complex_formats:
            # Try Docling first, fall back to Native
            if self.docling.can_handle(path):
                result = self.docling.parse(path)
                result["engine"] = "docling"
                return result
            elif self.native.can_handle(path):
                result = self.native.parse(path)
                result["engine"] = "native_fallback"
                return result
        
        elif ext in media_formats:
            # Media requires Docling
            if self.docling.can_handle(path):
                result = self.docling.parse(path)
                result["engine"] = "docling"
                return result
            else:
                return {
                    "success": False,
                    "error": f"Media parsing requires Docling. Run: pip install docling",
                    "content": "",
                    "elements": [],
                    "metadata": {"source": str(path)},
                    "engine": "none"
                }
        
        else:
            # Unknown format → try Native as text
            result = self.native.parse(path)
            result["engine"] = "native_guess"
            return result
    
    def extract_knowledge(self, parse_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract knowledge entries from a parse result.
        
        Returns a list of knowledge entries suitable for storage
        in the nexus_knowledge table.
        """
        if not parse_result.get("success"):
            return []
        
        entries = []
        metadata = parse_result.get("metadata", {})
        source = metadata.get("source", "unknown")
        
        # Create entry for each significant element
        for element in parse_result.get("elements", []):
            elem_type = element.get("type", "unknown")
            content = element.get("content", "")
            
            if content and len(content) > 20:  # Skip tiny elements
                entries.append({
                    "source": source,
                    "type": elem_type,
                    "content": content[:1000],  # Truncate for storage
                    "metadata": {
                        "index": element.get("index"),
                        "page": element.get("page"),
                        "parser": parse_result.get("engine")
                    }
                })
        
        # Create summary entry for the whole document
        full_content = parse_result.get("content", "")
        if full_content and len(full_content) > 100:
            summary = full_content[:500]
            if len(full_content) > 500:
                summary += "..."
            
            entries.insert(0, {
                "source": source,
                "type": "document_summary",
                "content": summary,
                "metadata": {
                    "total_elements": len(parse_result.get("elements", [])),
                    "parser": parse_result.get("engine"),
                    "format": parse_result.get("format")
                }
            })
        
        return entries
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            "version": self.VERSION,
            "parse_count": self._parse_count,
            "error_count": self._error_count,
            "docling_available": self.docling_available,
            "backends": {
                "docling": "available" if self.docling_available else "not installed",
                "native": "always available"
            }
        }
    
    def to_json(self, file_path: Union[str, Path]) -> str:
        """Parse and return JSON string."""
        result = self.parse(file_path)
        return json.dumps(result, indent=2, default=str)


# Singleton instance
_engine = None

def get_adis_engine() -> ADISEngine:
    """Get or create the ADIS engine singleton."""
    global _engine
    if _engine is None:
        _engine = ADISEngine()
    return _engine


# Convenience function
def parse(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Parse a document using ADIS."""
    return get_adis_engine().parse(file_path)
