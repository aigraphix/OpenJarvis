"""task_advanced_parse.py

Advanced Data Intelligence: High-Fidelity Document Parsing

Purpose:
- Parse a document into structured elements (Sections, Tables, Figures).
- Supports PDFs (via pypdf) and Markdown/text.
- Prepare data for persistence in a structured schema format.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import markdown
from bs4 import BeautifulSoup, Tag

# Local lightweight task logger (standalone; avoids external imports)
class AutomationAgentTask:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.started_at = None

    def start(self):
        self.started_at = time.time()

    def step(self, name: str, fn):
        started = time.time()
        out = fn()
        _ = time.time() - started
        return out

    def finish(self, success: bool, final_result: Any):
        _ = success
        _ = final_result


def extract_text(input_path: Path) -> str:
    """Extract UTF-8 text from supported input files.

    Supports:
    - .pdf via pypdf (requires venv deps)
    - text files (utf-8)
    """
    if input_path.suffix.lower() == ".pdf":
        # pypdf is optional at runtime; only required for PDFs
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(input_path))
        parts: List[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n\n".join(parts).strip()

    return input_path.read_text(encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--input", type=str, required=True)
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Advanced Intelligence: Document Parse",
        description="Parsing document into structured schema-aligned elements."
    )

    if not args.run:
        print("[AdvancedIntelligence] Prepared mode. Use --run.")
        return 0

    task.start()

    try:
        input_path = Path(args.input).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # 1. Convert to HTML (Stage 1 Parsing)
        def stage1():
            text = extract_text(input_path)
            html = markdown.markdown(text, extensions=['extra', 'tables'])
            return html
        
        html_content = task.step("Stage 1: Markdown to HTML Conversion", stage1)

        # 2. Extract Elements (Stage 2 Parsing - Advanced Logic)
        def stage2():
            soup = BeautifulSoup(html_content, 'html.parser')
            elements = []
            
            # Map HTML elements to Schema labels
            for i, child in enumerate(soup.contents):
                if not isinstance(child, Tag): continue
                
                label = 'paragraph'
                if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    label = 'section'
                elif child.name == 'table':
                    label = 'table'
                elif child.name in ['img', 'figure']:
                    label = 'figure'
                elif child.name == 'pre':
                    label = 'code'
                
                elements.append({
                    "reading_order": i,
                    "label": label,
                    "content": child.get_text().strip() if label != 'table' else str(child),
                    "tag": child.name
                })
            
            return elements

        extracted = task.step("Stage 2: Advanced Element Extraction", stage2)

        # 3. Persistence Mapping (Schema Alignment)
        def align():
            # This mimics the doc_parsed_elements table structure
            meta = {
                "log_id": f"sim-log-{int(time.time())}",
                "page_count": 1,
                "element_count": len(extracted)
            }
            return {"meta": meta, "elements": extracted}

        final = task.step("Schema-Alignment & Mapping", align)
        
        task.finish(success=True, final_result=final)
        print(json.dumps(final, ensure_ascii=False, indent=2))
        print(f"\n[Advanced Intelligence] Successfully parsed {len(extracted)} elements.")
        return 0

    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise

if __name__ == "__main__":
    main()
