#!/usr/bin/env python3
"""task_pdf_gen.py

AI PDF Builder: Professionally formatted documents via Pandoc & LaTeX.

Purpose:
- Generate high-fidelity PDFs from Markdown.
- Support templates for Whitepapers, Term Sheets, and Agreements.
- Integrate with the Automation Agent framework for verifiable artifacts.
"""

from __future__ import annotations

import argparse
import subprocess
import time
import sqlite3
import json
import os
from pathlib import Path
from typing import Dict, Any

# Reuse Automation Agent task wrapper (shared Brain logging).
# This skill does not define its own task wrapper.
from pathlib import Path as _Path
import sys as _sys

_AUTOMATION_ROOT = _Path(__file__).resolve().parents[2] / "antigravity-automation"
_sys.path.insert(0, str(_AUTOMATION_ROOT))
from lib import AutomationAgentTask  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "reports" / "artifacts"
# Prefer project-local brain for Mission Control portability
BRAIN_DB = str((REPO_ROOT / ".agent" / "working_memory.db"))


def brain_set_state(key: str, value: dict, source: str = "pdf-builder") -> None:
    """Best-effort state write for capability certification."""
    try:
        conn = sqlite3.connect(BRAIN_DB)
        cur = conn.cursor()
        now = int(time.time())
        cur.execute(
            "INSERT INTO state(key,value,updated_at,source) VALUES (?,?,?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at, source=excluded.source",
            (key, json.dumps(value, ensure_ascii=False), now, source),
        )
        conn.commit()
        conn.close()
    except Exception:
        # Don't fail the PDF generation if brain logging isn't available.
        pass

class PDFBuilder:
    def __init__(self, task: AutomationAgentTask):
        self.task = task

    def check_requirements(self):
        """Check for pandoc and pdflatex."""
        pandoc_check = subprocess.run(["which", "pandoc"], capture_output=True, text=True)
        pdflatex_check = subprocess.run(["which", "pdflatex"], capture_output=True, text=True)

        return {
            "pandoc": pandoc_check.returncode == 0,
            "pandoc_path": pandoc_check.stdout.strip(),
            "pdflatex": pdflatex_check.returncode == 0,
            "pdflatex_path": pdflatex_check.stdout.strip(),
        }

    def generate(self, input_md: Path, output_pdf: Path, doc_type: str = "memo", metadata: Dict[str, str] = None):
        """Run pandoc to generate the PDF."""
        cmd = [
            "pandoc",
            str(input_md),
            "-o", str(output_pdf),
            "--pdf-engine=pdflatex",
            "-V", f"mainfont=Helvetica",
            "-V", f"geometry:margin=1in"
        ]
        
        if metadata:
            for key, value in metadata.items():
                cmd.extend(["-V", f"{key}={value}"])

        # Add some default professional styling via LaTeX variables
        if doc_type == "whitepaper":
            cmd.extend(["-V", "titlepage=true", "-V", "toc=true"])
        elif doc_type == "memo":
            cmd.extend(["-V", "header-left=MEMORANDUM"])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Pandoc failed: {result.stderr}")
        
        return output_pdf

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--input", type=str, help="Input Markdown file")
    ap.add_argument("--type", type=str, default="memo", choices=["whitepaper", "memo", "agreement", "termsheet", "safe"])
    ap.add_argument("--title", type=str, default="Document")
    ap.add_argument("--author", type=str, default="Nexus AI")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="PDF Builder: Professional Generation",
        description=f"Generating {args.type} PDF using Pandoc."
    )

    if not args.run:
        print("[PDFBuilder] Prepared mode. Use --run.")
        return 0

    task.start()

    builder = PDFBuilder(task)
    
    # 1. Verification
    def check_env():
        status = builder.check_requirements()

        # Record environment status (best-effort) so the Brain reflects readiness.
        brain_set_state(
            "automation_agent.capabilities.pdf_builder.env",
            {
                "pandoc": status.get("pandoc"),
                "pandoc_path": status.get("pandoc_path"),
                "pdflatex": status.get("pdflatex"),
                "pdflatex_path": status.get("pdflatex_path"),
            },
            source="pdf-builder",
        )

        if not status["pandoc"]:
            raise RuntimeError(
                "Pandoc is not installed. Install: `brew install pandoc`."
            )

        # Clean handling for missing LaTeX engine: fail early with a clear message.
        if not status["pdflatex"]:
            raise RuntimeError(
                "pdflatex is not available (BasicTeX missing). Install: `brew install --cask basictex` "
                "then restart your terminal (or run: eval \"$(/usr/libexec/path_helper)\")."
            )

        return {"status": "Full Stack Ready", **status}

    env_status = task.step("Environment Verification", check_env)

    # 2. Input Prep
    def prep_input():
        if args.input:
            input_path = Path(args.input).resolve()
        else:
            # Create a sample if none provided
            temp_md = OUTPUT_DIR / "temp_doc.md"
            temp_md.write_text(f"# {args.title}\n\n**Author:** {args.author}\n\nThis is a professional document generated via the AI PDF Builder skill.")
            input_path = temp_md
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        return str(input_path)

    input_file = task.step("Input Preparation", prep_input)

    # 3. Execution
    def execute():
        ts = time.strftime("%Y-%m-%d-%H%M%S")
        out_file = OUTPUT_DIR / f"{args.type}-{ts}.pdf"
        
        metadata = {
            "title": args.title,
            "author": args.author,
            "date": time.strftime("%B %d, %Y")
        }
        
        pdf_path = builder.generate(Path(input_file), out_file, doc_type=args.type, metadata=metadata)
        return str(pdf_path)

    pdf_result = task.step("Pandoc Rendering Engine", execute)

    # Mark capability as verified (best-effort): we successfully produced a PDF artifact.
    brain_set_state(
        "automation_agent.capabilities.pdf_builder",
        {
            "status": "VERIFIED",
            "engine": "pandoc+pdflatex",
            "pdf_path": pdf_result,
            "env": env_status,
        },
        source="pdf-builder",
    )

    task.finish(success=True, final_result={"pdf_path": pdf_result, "env": env_status})
    print(f"\n[PDFBuilder Success] Document generated: {pdf_result}")

if __name__ == "__main__":
    main()
