#!/usr/bin/env python3
"""Nexus Self-Test (Scheduled)

Goals
- Run a lightweight self-test prompt against all configured agents
- Collect results in a single structured log file (JSONL)
- If any agent fails, trigger a notification path (email placeholder)

Notes
- This script intentionally keeps the test prompt simple and machine-parseable.
- It calls the Nexus CLI via subprocess.
- Email wiring is a stub: we record that an email would be sent.

Typical usage
  python skills/nexus-selftest/scripts/scheduled_test.py --email ops@example.com

Exit codes
- 0: all pass
- 2: one or more failures
- 3: CLI/runtime error
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SELFTEST_PROMPT = (
    "Run SELF-TEST: "
    "1) State your role "
    "2) Confirm tool access (list one file) "
    "3) Output JSON: {\"agent\":\"<agent_id>\",\"test\":\"pass\"}. "
    "Report: PASS/FAIL per item."
)


def repo_root() -> Path:
    # .../skills/nexus-selftest/scripts/scheduled_test.py -> repo root is 4 parents up
    return Path(__file__).resolve().parents[3]


def run_cmd(
    args: List[str],
    cwd: Optional[Path] = None,
    timeout_s: int = 600,
) -> Tuple[int, str, str]:
    p = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout_s,
    )
    return p.returncode, p.stdout, p.stderr


def _extract_json(text: str) -> Any:
    """Best-effort JSON extraction.

    Some CLIs (notably dotenv) may print informational lines to stdout even in
    --json mode, which breaks naive json.loads(stdout).

    Strategy: scan for the first position that can be JSON-decoded.
    """
    s = text.lstrip("\ufeff")
    dec = json.JSONDecoder()

    candidates: List[int] = []
    for ch in ("{", "["):
        start = 0
        while True:
            i = s.find(ch, start)
            if i == -1:
                break
            candidates.append(i)
            start = i + 1
    candidates.sort()

    last_err: Optional[Exception] = None
    for i in candidates:
        try:
            obj, _idx = dec.raw_decode(s[i:])
            return obj
        except Exception as e:
            last_err = e
            continue

    raise ValueError(
        f"Failed to locate valid JSON in output (last_err={last_err}): {s[:2000]}"
    )


def list_agents(cwd: Path) -> List[str]:
    # Prefer JSON output for stability.
    code, out, err = run_cmd(["pnpm", "-s", "nexus", "agents", "list", "--json"], cwd=cwd)
    if code != 0:
        raise RuntimeError(f"Failed to list agents (code={code}): {err.strip()}")
    data = _extract_json(out)

    # Expected: { ok: true, agents: [...] } or just { agents: [...] }
    agents = data.get("agents") if isinstance(data, dict) else None
    if not isinstance(agents, list):
        # fallback: sometimes JSON output might just be an array
        if isinstance(data, list):
            agents = data
        else:
            raise RuntimeError(f"Unexpected agents list JSON shape: {type(data)}")

    ids: List[str] = []
    for a in agents:
        if isinstance(a, dict) and isinstance(a.get("id"), str):
            ids.append(a["id"])
        elif isinstance(a, str):
            ids.append(a)

    # De-dup, stable order
    seen = set()
    out_ids: List[str] = []
    for agent_id in ids:
        if agent_id in seen:
            continue
        seen.add(agent_id)
        out_ids.append(agent_id)
    return out_ids


def run_agent_selftest(
    cwd: Path,
    agent_id: str,
    local: bool,
    timeout_s: int,
) -> Dict[str, Any]:
    args = ["pnpm", "-s", "nexus", "agent", "--agent", agent_id, "--message", SELFTEST_PROMPT, "--json"]
    if local:
        args.append("--local")

    code, out, err = run_cmd(args, cwd=cwd, timeout_s=timeout_s)

    record: Dict[str, Any] = {
        "agent": agent_id,
        "ok": False,
        "exitCode": code,
        "raw": None,
        "error": None,
        "ts": dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat(),
    }

    if code != 0:
        record["error"] = err.strip() or out.strip() or f"nexus agent exited with code={code}"
        return record

    # Parse JSON output from CLI
    try:
        payload = _extract_json(out)
        record["raw"] = payload
    except Exception as e:
        record["error"] = f"Failed to parse nexus agent JSON output: {e}: {out[:5000]}"
        return record

    # Best-effort: treat any successful command as ok unless content indicates FAIL
    text = ""
    if isinstance(record["raw"], dict):
        # Common patterns: result.reply, data.reply, etc.
        for key in ("reply", "text", "message", "output"):
            if isinstance(record["raw"].get(key), str):
                text = record["raw"][key]
                break
        if not text:
            # sometimes nested
            data = record["raw"].get("data")
            if isinstance(data, dict):
                for key in ("reply", "text", "message", "output"):
                    if isinstance(data.get(key), str):
                        text = data[key]
                        break

    lowered = text.lower()
    if "result: fail" in lowered or "fail" in lowered and "result: pass" not in lowered:
        # intentionally conservative; you can tighten parsing later.
        record["ok"] = False
        record["error"] = "Self-test output indicates failure"
        record["selftestText"] = text[:20000]
        return record

    record["ok"] = True
    record["selftestText"] = text[:20000] if text else None
    return record


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def send_failure_email(to_addr: str, subject: str, body: str, cwd: Path) -> bool:
    """Send email using gog (Google Workspace CLI) Gmail.
    
    Returns True if email sent successfully, False otherwise.
    """
    try:
        # Use gog gmail send with --body flag
        cmd = [
            "gog", "gmail", "send",
            "--to", to_addr,
            "--subject", subject,
            "--body", body,
            "--client", "nexus",
            "--no-input",
            "--force",
        ]
        
        p = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )
        
        if p.returncode == 0:
            sys.stdout.write(f"[SELFTEST] Email sent to {to_addr}\n")
            return True
        else:
            sys.stderr.write(f"[SELFTEST] Email failed: {p.stderr.strip() or p.stdout.strip()}\n")
            return False
            
    except Exception as e:
        sys.stderr.write(f"[SELFTEST] Email error: {e}\n")
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", default="", help="Email address to notify on any failures")
    ap.add_argument("--local", action="store_true", help="Run via embedded agent (--local)")
    ap.add_argument("--timeout", type=int, default=600, help="Timeout per agent turn (seconds)")
    ap.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Optional list of agent IDs to test (default: all)",
    )
    args = ap.parse_args()

    root = repo_root()
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # Logs live in the main workspace (repo root workspace/), per user request.
    log_dir = root / "workspace" / "selftest" / "scheduled"
    log_path = log_dir / f"scheduled-selftest-{timestamp}.jsonl"

    try:
        agent_ids = list_agents(root)
    except Exception as e:
        sys.stderr.write(f"[SELFTEST] ERROR: {e}\n")
        return 3

    if args.only is not None and len(args.only) > 0:
        wanted = set(args.only)
        agent_ids = [a for a in agent_ids if a in wanted]

    results: List[Dict[str, Any]] = []
    for agent_id in agent_ids:
        sys.stdout.write(f"[SELFTEST] Running: {agent_id}\n")
        try:
            rec = run_agent_selftest(root, agent_id, local=args.local, timeout_s=args.timeout)
        except subprocess.TimeoutExpired:
            rec = {
                "agent": agent_id,
                "ok": False,
                "exitCode": None,
                "error": f"Timeout after {args.timeout}s",
                "ts": dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat(),
            }
        except Exception as e:
            rec = {
                "agent": agent_id,
                "ok": False,
                "exitCode": None,
                "error": f"Unhandled error: {e}",
                "ts": dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat(),
            }
        results.append(rec)

    write_jsonl(log_path, results)
    sys.stdout.write(f"[SELFTEST] Wrote log: {log_path}\n")

    failures = [r for r in results if not r.get("ok")]
    if failures:
        summary = {
            "run": timestamp,
            "failures": [{"agent": f.get("agent"), "error": f.get("error")} for f in failures],
            "log": str(log_path),
        }
        subject = f"Nexus self-test failures ({len(failures)}/{len(results)})"
        body = json.dumps(summary, indent=2)

        if args.email.strip():
            send_failure_email(args.email.strip(), subject, body, root)
        else:
            sys.stderr.write("[SELFTEST] Failures detected but --email not provided.\n")
            sys.stderr.write(body + "\n")

        return 2

    sys.stdout.write(f"[SELFTEST] All agents passed ({len(results)})\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
