#!/usr/bin/env python3
"""task_notion_verify.py

Automation Agent task: verify Notion integration (Knowledge Ops P1).

Evidence goals:
- Confirm a Notion API key source exists (env var or ~/.config/notion/api_key)
- Make a read-only API call (POST /v1/search with empty query)
- Log success/failure and a minimal summary to the Brain.

Safe defaults:
- Prepared/no-op unless --run

Usage:
  python3 runner.py task_notion_verify.py --run

Optional:
  --query "Automation Agent"   # search term
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from lib import AutomationAgentTask

NOTION_VERSION = "2025-09-03"
NOTION_KEY_FILE = Path.home() / ".config" / "notion" / "api_key"


def load_key() -> Optional[str]:
    env = (os.environ.get("NOTION_API_KEY") or "").strip()
    if env:
        return env
    if NOTION_KEY_FILE.exists():
        return NOTION_KEY_FILE.read_text(encoding="utf-8", errors="replace").strip()
    return None


def run_curl_search(key: str, query: str) -> Dict[str, Any]:
    body = {"query": query} if query else {}
    cmd = [
        "curl",
        "-sS",
        "-X",
        "POST",
        "https://api.notion.com/v1/search",
        "-H",
        f"Authorization: Bearer {key}",
        "-H",
        f"Notion-Version: {NOTION_VERSION}",
        "-H",
        "Content-Type: application/json",
        "--data-binary",
        json.dumps(body),
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return {"cmd": cmd, "exit_code": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def summarize_search(stdout: str) -> Dict[str, Any]:
    try:
        obj = json.loads(stdout)
    except Exception as e:
        return {"ok": False, "error": f"JSON parse failed: {e}", "stdout_snip": stdout[:200]}

    # Notion errors usually have an "object": "error"
    if isinstance(obj, dict) and obj.get("object") == "error":
        return {
            "ok": False,
            "notion_error": {
                "status": obj.get("status"),
                "code": obj.get("code"),
                "message": obj.get("message"),
            },
        }

    results = obj.get("results") if isinstance(obj, dict) else None
    return {
        "ok": True,
        "results_count": len(results) if isinstance(results, list) else None,
        "has_next": obj.get("has_more") if isinstance(obj, dict) else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--query", type=str, default="")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Notion Verification (Knowledge Ops)",
        description="Verify Notion API key + read-only search call.",
    )

    if not args.run:
        print("[AutomationAgent] Prepared mode. Use --run to execute.")
        return 0

    task.start()

    try:
        key = task.step("Load Notion API Key", load_key)
        key_present = bool(key and str(key).strip())
        key_source = "env:NOTION_API_KEY" if (os.environ.get("NOTION_API_KEY") or "").strip() else ("file:~/.config/notion/api_key" if NOTION_KEY_FILE.exists() else "missing")

        if not key_present:
            task.finish(success=False, final_result={"error": "Missing NOTION_API_KEY and ~/.config/notion/api_key", "key_source": key_source})
            print("Missing Notion API key (NOTION_API_KEY or ~/.config/notion/api_key)")
            return 2

        raw = task.step("Notion API Search (read-only)", run_curl_search, key, args.query)
        summary = task.step("Summarize Response", summarize_search, raw.get("stdout", ""))

        ok = bool(summary.get("ok"))
        final = {
            "status": "VERIFIED" if ok else "FAILED",
            "key_source": key_source,
            "query": args.query,
            "summary": summary,
        }

        task.finish(success=ok, final_result=final)
        print(json.dumps(final, indent=2))
        return 0 if ok else 1

    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
