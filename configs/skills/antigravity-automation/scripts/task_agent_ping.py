#!/usr/bin/env python3
"""task_agent_ping.py

Nexus Link: High-Fidelity Inter-Agent Wake Protocol.

Purpose:
- Enable Antigravity to "Wake up" Nexus (CLI).
- Enable Nexus to "Wake up" Antigravity (IDE) via Signal.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path

from lib import AutomationAgentTask

REPO_ROOT = Path(__file__).resolve().parents[3]
SIGNAL_FILE = REPO_ROOT / ".agent" / "nexus_signals.json"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--target", choices=["nexus", "antigravity"], required=True)
    ap.add_argument("--message", type=str, default="Nexus Handshake: Wake Signal Received.")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name=f"Nexus Link: Wake {args.target}",
        description=f"Sending inter-agent signal to {args.target}."
    )

    if not args.run:
        print(f"[NexusLink] Prepared to wake {args.target}. Use --run.")
        return 0

    task.start()

    if not SIGNAL_FILE.parent.exists():
        SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing signals
    signals = {}
    if SIGNAL_FILE.exists():
        try:
            with open(SIGNAL_FILE, 'r') as f:
                signals = json.load(f)
        except:
            pass

    def send_signal():
        ts = time.time()
        signals[args.target] = {
            "status": "WAKE",
            "timestamp": ts,
            "message": args.message,
            "sender": "Antigravity" if args.target == "nexus" else "Nexus"
        }
        with open(SIGNAL_FILE, 'w') as f:
            json.dump(signals, f, indent=2)
            
        # Physical Wake-up Triggers
        if args.target == "nexus":
            # Wake the CLI via pnpm agent deliver (if gateway is online)
            subprocess.run([
                "pnpm", "nexus", "agent", 
                "--agent", "main", 
                "--message", f"📢 NEXUS WAKE: {args.message}", 
                "--deliver"
            ], capture_output=True)
            return "Signal sent to Nexus via Gateway."
        else:
            # Wake Antigravity via macOS Notification (Visible to User/Architect)
            script = f'display notification "{args.message}" with title "Nexus Wake: Antigravity Summoned"'
            subprocess.run(["osascript", "-e", script])
            return "Signal written to Mailbox. macOS Notification Pushed."

    result = task.step(f"Transmitting Wake Signal to {args.target}", send_signal)

    task.finish(success=True, final_result={"status": "Signal Delivered", "detail": result})
    print(f"\n[Nexus Success] {result}")

if __name__ == "__main__":
    main()
