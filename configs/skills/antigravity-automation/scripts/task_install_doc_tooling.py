#!/usr/bin/env python3
"""task_install_doc_tooling.py

Automation Agent task: self-installation capability test.

Installs Python libraries required for DOCX/PDF generation:
- python-docx
- reportlab

Default install strategy (safe-ish): pip user install (no sudo)
  python3 -m pip install --user python-docx reportlab

This avoids mutating system Python site-packages.

Usage:
  python3 runner.py task_install_doc_tooling.py --run

Notes:
- Records pip output to Brain via AutomationAgentTask.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Dict, Any

from lib import AutomationAgentTask


def run(cmd, timeout_s: int = 600) -> Dict[str, Any]:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    return {
        "cmd": cmd,
        "exit_code": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Tooling Install Test (python-docx + reportlab)",
        description="Install python-docx and reportlab via pip --user and verify imports.",
    )

    if not args.run:
        print("[AutomationAgent] Prepared mode. Use --run to execute.")
        return 0

    task.start()
    try:
        task.step("Python Version", run, [sys.executable, "-V"], 30)
        task.step("Pip Version", run, [sys.executable, "-m", "pip", "-V"], 30)
        task.step(
            "Install Packages (pip --user)",
            run,
            [sys.executable, "-m", "pip", "install", "--user", "python-docx", "reportlab"],
            600,
        )
        task.step(
            "Verify Imports",
            run,
            [
                sys.executable,
                "-c",
                "import docx; import reportlab; print('imports_ok')",
            ],
            60,
        )

        task.finish(success=True, final_result={"status": "COMPLETED", "note": "Installed python-docx and reportlab (pip --user)"})
        return 0
    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
