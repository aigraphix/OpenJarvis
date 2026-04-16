#!/usr/bin/env python3
"""
NEXUS-ADIS CLI Parser
Advanced Data Intelligence System - Command Line Interface

Usage:
    python3 adis_parse.py --input <file_path> [--output <output_path>] [--format json|text]
    python3 adis_parse.py --help
    python3 adis_parse.py --stats
"""

import argparse
import json
import sys
from pathlib import Path

# Add skill lib to path for imports
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))

from lib.backends.docling_backend import get_docling_backend
from lib.backends.native_backend import get_native_backend


VERSION = "3.0"


class ADISParser:
    """CLI wrapper for ADIS parsing."""
    
    def __init__(self):
        self.docling = get_docling_backend()
        self.native = get_native_backend()
    
    def parse(self, file_path: Path) -> dict:
        """Parse a file using the best available backend."""
        ext = file_path.suffix.lower()
        
        # Simple formats → Native
        simple = {".txt", ".md", ".markdown", ".json", ".yaml", ".yml", ".csv", ".tsv"}
        
        # Complex formats → Docling preferred
        complex_exts = {".pdf", ".docx", ".pptx", ".xlsx", ".html"}
        
        if ext in simple:
            result = self.native.parse(file_path)
            result["engine"] = "native"
        elif ext in complex_exts and self.docling.available:
            result = self.docling.parse(file_path)
            result["engine"] = "docling"
        elif ext in complex_exts:
            # Fallback to native PDF
            result = self.native.parse(file_path)
            result["engine"] = "native_fallback"
        else:
            result = self.native.parse(file_path)
            result["engine"] = "native"
        
        result["adis_version"] = VERSION
        return result
    
    def get_stats(self) -> dict:
        """Get parser stats."""
        return {
            "version": VERSION,
            "docling_available": self.docling.available,
            "native_available": True,
            "supported_formats": {
                "docling": list(self.docling.SUPPORTED_EXTENSIONS) if self.docling.available else [],
                "native": list(self.native.SUPPORTED_EXTENSIONS)
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description="NEXUS-ADIS Document Parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 adis_parse.py --input document.pdf
    python3 adis_parse.py --input data.json --output parsed.json
    python3 adis_parse.py --stats
        """
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Path to file to parse"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "text", "summary"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show parser statistics"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version"
    )
    
    args = parser.parse_args()
    
    adis = ADISParser()
    
    # Handle version
    if args.version:
        print(f"NEXUS-ADIS v{VERSION}")
        sys.exit(0)
    
    # Handle stats
    if args.stats:
        stats = adis.get_stats()
        print(json.dumps(stats, indent=2))
        sys.exit(0)
    
    # Require input for parsing
    if not args.input:
        parser.print_help()
        sys.exit(1)
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse the file
    result = adis.parse(input_path)
    
    # Format output
    if args.format == "json":
        output = json.dumps(result, indent=2, default=str)
    elif args.format == "text":
        output = result.get("content", "")
    elif args.format == "summary":
        output = f"""
NEXUS-ADIS Parse Result
=======================
File: {result.get('metadata', {}).get('filename', 'unknown')}
Engine: {result.get('engine', 'unknown')}
Success: {result.get('success', False)}
Format: {result.get('format', 'unknown')}
Elements: {len(result.get('elements', []))}

Content Preview:
{result.get('content', '')[:500]}...
"""
    else:
        output = json.dumps(result, indent=2)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding="utf-8")
        print(f"✅ Output written to: {output_path}")
    else:
        print(output)
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
