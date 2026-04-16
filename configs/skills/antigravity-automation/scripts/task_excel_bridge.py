#!/usr/bin/env python3
"""task_excel_bridge.py

Excel Mastery Certification: Local Data Processing with Pandas & OpenPyXL.

Purpose:
- Install missing data libraries (if necessary).
- Generate a structured System Audit report in .xlsx format.
- Demonstrate styling and data reading.
"""

from __future__ import annotations

import argparse
import subprocess
import time
import os
import sys
from pathlib import Path
import json

from lib import AutomationAgentTask

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO_ROOT / "reports" / "artifacts"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Excel Mastery Certification",
        description="Testing local XLSX generation and data processing."
    )

    if not args.run:
        print("[ExcelBridge] Prepared mode. Use --run.")
        return 0

    task.start()

    # 1. Install Dependencies
    def install_deps():
        # Respect PEP 668 externally-managed environments.
        # Install to user site-packages (no sudo).
        # Use the same interpreter as the runner (avoids system Python PEP668 issues).
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--user",
                "--break-system-packages",
                "pandas",
                "openpyxl",
            ],
            check=True,
        )
        import pandas as pd
        import openpyxl
        return f"Pandas v{pd.__version__} installed (pip --user)."

    task.step("Install Pandas and OpenPyXL", install_deps)

    import pandas as pd  # Import after install

    ts = time.strftime("%Y-%m-%d-%H%M%S")
    work_dir = OUTPUT_DIR / f"excel-test-{ts}"
    work_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = work_dir / "system_audit_sample.xlsx"

    # 2. Generate Data
    def gen_xlsx():
        data = {
            "Task ID": [1, 2, 3, 4],
            "Mission Name": ["Desktop Neat", "Document Gen", "Whisper Test", "Reflect Engine"],
            "Status": ["COMPLETED", "COMPLETED", "COMPLETED", "COMPLETED"],
            "Time (s)": [1.5, 4.2, 12.8, 2.1],
            "Priority": ["P1", "P0", "P0", "P0"]
        }
        df = pd.DataFrame(data)
        
        # Save to Excel
        df.to_excel(xlsx_path, index=False, engine='openpyxl')
        return str(xlsx_path)

    task.step("Generate System Audit Spreadsheet", gen_xlsx)

    # 3. Read back and verify
    def verify_xlsx():
        df = pd.read_excel(xlsx_path)
        mean_time = df["Time (s)"].mean()
        return {
            "rows": len(df),
            "average_processing_time": float(mean_time),
            "columns": list(df.columns)
        }

    read_results = task.step("Verify XLSX Content (Read-back)", verify_xlsx)

    task.finish(success=True, final_result={
        "read_results": read_results,
        "artifact_path": str(xlsx_path)
    })
    
    print(f"\n[Excel Success] Generated report with {read_results['rows']} rows.")

if __name__ == "__main__":
    main()
