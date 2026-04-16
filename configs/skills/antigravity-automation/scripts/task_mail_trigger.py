#!/usr/bin/env python3
"""task_mail_trigger.py

P1: Apple Mail / Calendar Integration (Local Triggering)

Goal
- Provide a local-first trigger surface for Automation Agent tasks based on:
  - Apple Mail inbox state (unread counts / latest subjects)
  - Apple Calendar upcoming events (next N events)

Design principles
- Read-only by default (Zero-Touch friendly).
- Evidence-first: log findings to the Brain via AutomationAgentTask.
- No external APIs / no paid keys.

Current scope (v0)
- Mail: unread message count + optionally subjects for most recent unread.
- Calendar: upcoming events in next X hours.

Usage
  python3 runner.py task_mail_trigger.py --run --mode mail
  python3 runner.py task_mail_trigger.py --run --mode calendar --hours 24

Notes
- Requires macOS Automation permissions for Terminal/Python to control Mail/Calendar.
- Uses `osascript` (AppleScript). JXA can be added later.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from typing import Any, Dict

from lib import AutomationAgentTask


def run_osascript(script: str, timeout_s: int = 60) -> Dict[str, Any]:
    p = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )
    return {
        "exit_code": p.returncode,
        "stdout": (p.stdout or "").strip(),
        "stderr": (p.stderr or "").strip(),
    }


def mail_unread_summary(limit: int = 5) -> Dict[str, Any]:
    # Apple Mail scripting is a bit finicky; keep to simple queries.
    # This script returns a JSON-like string (not strict JSON) that we parse lightly.
    script = f'''
    tell application "Mail"
      set unreadCount to unread count of inbox
      set msgs to (messages of inbox whose read status is false)
      set subjList to {{}}
      set n to {int(limit)}
      repeat with i from 1 to (count of msgs)
        if i > n then exit repeat
        set m to item i of msgs
        set end of subjList to (subject of m)
      end repeat
      return "unread_count=" & unreadCount & "\nsubjects=" & subjList
    end tell
    '''

    res = run_osascript(script)
    if res["exit_code"] != 0:
        return {"ok": False, "error": res["stderr"] or "osascript failed", "raw": res}

    out = res["stdout"]
    unread = None
    subjects = []
    for line in out.splitlines():
        if line.startswith("unread_count="):
            try:
                unread = int(line.split("=", 1)[1].strip())
            except Exception:
                unread = None
        if line.startswith("subjects="):
            # AppleScript list prints like: {"a", "b"}
            subj_raw = line.split("=", 1)[1].strip()
            subj_raw = subj_raw.strip("{}")
            if subj_raw:
                # naive split (OK for v0)
                subjects = [s.strip().strip('"') for s in subj_raw.split(",") if s.strip()]

    return {"ok": True, "unread_count": unread, "subjects": subjects}


def calendar_upcoming_summary(hours: int = 24, limit: int = 10) -> Dict[str, Any]:
    # Use Calendar app (notion: may require permissions). We focus on upcoming events.
    # Returns event summaries (title + start date) from the default calendar set.
    script = f'''
    set nowDate to (current date)
    set endDate to (nowDate + ({int(hours)} * hours))

    tell application "Calendar"
      set evs to {{}}
      set cals to calendars
      repeat with cal in cals
        try
          set calEvs to (events of cal whose start date ≥ nowDate and start date ≤ endDate)
          repeat with e in calEvs
            set end of evs to (summary of e & "|" & (start date of e as string))
          end repeat
        end try
      end repeat

      -- trim
      set outList to {{}}
      set n to {int(limit)}
      repeat with i from 1 to (count of evs)
        if i > n then exit repeat
        set end of outList to item i of evs
      end repeat

      return outList
    end tell
    '''

    res = run_osascript(script, timeout_s=120)
    if res["exit_code"] != 0:
        return {"ok": False, "error": res["stderr"] or "osascript failed", "raw": res}

    # Output comes back as comma-separated list of strings.
    raw = res["stdout"]
    items = [x.strip() for x in raw.split(",") if x.strip()]
    events = []
    for it in items:
        it = it.strip().strip('"')
        if "|" in it:
            title, start = it.split("|", 1)
            events.append({"title": title.strip(), "start": start.strip()})
        else:
            events.append({"title": it, "start": None})

    return {"ok": True, "hours": hours, "events": events}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--mode", choices=["mail", "calendar"], required=False)
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--hours", type=int, default=24)
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="P1 Trigger Probe (Mail/Calendar)",
        description="Local-first trigger probe for Apple Mail/Calendar (read-only).",
    )

    if not args.run:
        print("[TriggerProbe] Prepared mode. Use --run.")
        return 0

    if not args.mode:
        print("Error: --mode is required (mail|calendar)")
        return 1

    task.start()
    try:
        if args.mode == "mail":
            result = task.step("Mail unread summary", mail_unread_summary, args.limit)
        else:
            result = task.step("Calendar upcoming summary", calendar_upcoming_summary, args.hours, max(args.limit, 1))

        task.finish(success=bool(result.get("ok")), final_result=result)
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 2

    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
