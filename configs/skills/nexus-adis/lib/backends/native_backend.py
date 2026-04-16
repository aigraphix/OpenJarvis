"""
NEXUS-ADIS Native Backend
Lightweight document parsing using standard libraries

This backend handles simple formats without external dependencies:
- Markdown, Text files
- JSON, YAML
- CSV, TSV
- Basic PDF (text extraction only)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import csv
import io

# Optional imports with graceful degradation
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import markdown
    from bs4 import BeautifulSoup
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class NativeBackend:
    """
    Lightweight document parser using standard Python libraries.
    Always available as a fallback.
    """
    
    SUPPORTED_EXTENSIONS = {
        ".txt", ".md", ".markdown",
        ".json", ".yaml", ".yml",
        ".csv", ".tsv",
        ".pdf"  # Basic text extraction
    }
    
    def __init__(self):
        pass
    
    @property
    def available(self) -> bool:
        """Native backend is always available."""
        return True
    
    def can_handle(self, file_path: Path) -> bool:
        """Check if this backend can handle the file type."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a document using native parsers.
        
        Returns:
            Dict with:
            - success: bool
            - content: str (extracted text)
            - elements: List[Dict] (structured elements)
            - metadata: Dict (document metadata)
            - format: str (output format used)
        """
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "content": "",
                "elements": [],
                "metadata": {}
            }
        
        ext = file_path.suffix.lower()
        
        try:
            if ext in {".txt"}:
                return self._parse_text(file_path)
            elif ext in {".md", ".markdown"}:
                return self._parse_markdown(file_path)
            elif ext in {".json"}:
                return self._parse_json(file_path)
            elif ext in {".yaml", ".yml"}:
                return self._parse_yaml(file_path)
            elif ext in {".csv", ".tsv"}:
                return self._parse_csv(file_path, delimiter="," if ext == ".csv" else "\t")
            elif ext in {".pdf"}:
                return self._parse_pdf(file_path)
            else:
                return self._parse_text(file_path)  # Fallback to text
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "content": "",
                "elements": [],
                "metadata": {"source": str(file_path)}
            }
    
    def _parse_text(self, file_path: Path) -> Dict[str, Any]:
        """Parse plain text file."""
        content = file_path.read_text(encoding="utf-8")
        
        # Split into paragraphs as elements
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        elements = [
            {"type": "paragraph", "index": i, "content": p[:500]}
            for i, p in enumerate(paragraphs)
        ]
        
        return {
            "success": True,
            "content": content,
            "elements": elements,
            "metadata": {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "parser": "native_text",
                "char_count": len(content)
            },
            "format": "text"
        }
    
    def _parse_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Parse markdown file."""
        raw_content = file_path.read_text(encoding="utf-8")
        
        elements = []
        html_content = raw_content
        
        if MARKDOWN_AVAILABLE:
            # Convert to HTML and extract structure
            html_content = markdown.markdown(raw_content, extensions=["extra", "codehilite"])
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract headers
            for i, header in enumerate(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])):
                elements.append({
                    "type": "section",
                    "level": int(header.name[1]),
                    "index": i,
                    "content": header.get_text()[:200]
                })
            
            # Extract code blocks
            for i, code in enumerate(soup.find_all("code")):
                elements.append({
                    "type": "code",
                    "index": i,
                    "content": code.get_text()[:500]
                })
            
            # Extract tables
            for i, table in enumerate(soup.find_all("table")):
                rows = len(table.find_all("tr"))
                cols = len(table.find_all("th")) or len(table.find("tr").find_all("td") if table.find("tr") else [])
                elements.append({
                    "type": "table",
                    "index": i,
                    "rows": rows,
                    "cols": cols
                })
        
        return {
            "success": True,
            "content": raw_content,
            "elements": elements,
            "metadata": {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "parser": "native_markdown",
                "char_count": len(raw_content)
            },
            "format": "markdown"
        }
    
    def _parse_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse JSON file."""
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)
        
        # Extract top-level keys as elements
        elements = []
        if isinstance(data, dict):
            for i, (key, value) in enumerate(data.items()):
                elements.append({
                    "type": "field",
                    "index": i,
                    "key": key,
                    "value_type": type(value).__name__
                })
        elif isinstance(data, list):
            elements.append({
                "type": "array",
                "index": 0,
                "length": len(data),
                "item_type": type(data[0]).__name__ if data else "unknown"
            })
        
        return {
            "success": True,
            "content": json.dumps(data, indent=2),
            "elements": elements,
            "metadata": {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "parser": "native_json",
                "root_type": type(data).__name__
            },
            "format": "json"
        }
    
    def _parse_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Parse YAML file."""
        if not YAML_AVAILABLE:
            return {
                "success": False,
                "error": "PyYAML not installed. Run: pip install pyyaml",
                "content": "",
                "elements": [],
                "metadata": {}
            }
        
        content = file_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        
        elements = []
        if isinstance(data, dict):
            for i, (key, value) in enumerate(data.items()):
                elements.append({
                    "type": "field",
                    "index": i,
                    "key": key,
                    "value_type": type(value).__name__
                })
        
        return {
            "success": True,
            "content": content,
            "elements": elements,
            "metadata": {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "parser": "native_yaml"
            },
            "format": "yaml"
        }
    
    def _parse_csv(self, file_path: Path, delimiter: str = ",") -> Dict[str, Any]:
        """Parse CSV/TSV file."""
        content = file_path.read_text(encoding="utf-8")
        
        reader = csv.reader(io.StringIO(content), delimiter=delimiter)
        rows = list(reader)
        
        headers = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []
        
        elements = [{
            "type": "table",
            "index": 0,
            "rows": len(data_rows),
            "cols": len(headers),
            "headers": headers[:10]  # First 10 headers
        }]
        
        return {
            "success": True,
            "content": content,
            "elements": elements,
            "metadata": {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "parser": "native_csv",
                "row_count": len(data_rows),
                "col_count": len(headers)
            },
            "format": "csv"
        }
    
    def _parse_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF file (basic text extraction)."""
        if not PYPDF_AVAILABLE:
            return {
                "success": False,
                "error": "pypdf not installed. Run: pip install pypdf",
                "content": "",
                "elements": [],
                "metadata": {}
            }
        
        reader = PdfReader(str(file_path))
        pages = []
        elements = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(text)
            elements.append({
                "type": "page",
                "index": i,
                "char_count": len(text),
                "content": text[:200]
            })
        
        full_content = "\n\n---\n\n".join(pages)
        
        return {
            "success": True,
            "content": full_content,
            "elements": elements,
            "metadata": {
                "source": str(file_path),
                "filename": file_path.name,
                "extension": file_path.suffix,
                "parser": "native_pdf",
                "page_count": len(reader.pages)
            },
            "format": "text"
        }
    
    def to_json(self, file_path: Path) -> str:
        """Parse and return JSON-serializable result."""
        result = self.parse(file_path)
        return json.dumps(result, indent=2, default=str)


# Singleton instance
_backend = None

def get_native_backend() -> NativeBackend:
    """Get or create the Native backend singleton."""
    global _backend
    if _backend is None:
        _backend = NativeBackend()
    return _backend
