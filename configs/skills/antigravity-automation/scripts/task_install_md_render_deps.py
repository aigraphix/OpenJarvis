#!/usr/bin/env python3
"""task_install_md_render_deps.py

Automation Agent task: install Markdown rendering deps for proper rendering.

Installs (pip --user):
- markdown
- beautifulsoup4

Usage:
  python3 runner.py task_install_md_render_deps.py --run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from typing import Any, Dict

from lib import AutomationAgentTask


def run(cmd, timeout_s: int = 600) -> Dict[str, Any]:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    return {"cmd": cmd, "exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Install MD Render Deps (markdown + bs4)",
        description="Install markdown + beautifulsoup4 for proper MD→HTML→tree rendering.",
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
            [sys.executable, "-m", "pip", "install", "--user", "markdown", "beautifulsoup4"],
            600,
        )
        task.step(
            "Verify Imports",
            run,
            [sys.executable, "-c", "import markdown; import bs4; print('imports_ok')"],
            60,
        )
        task.finish(success=True, final_result={"status": "COMPLETED"})
        return 0
    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
