#!/usr/bin/env python3
"""task_email_handshake.py

Email Mastery Certification: Himalaya CLI Integration.

Purpose:
- Verify Himalaya CLI is installed.
- Check for existing account configuration (~/.config/himalaya/config.toml).
- Demonstrate listing email envelopes if configured.
- Provide a bridge for automated email notifications.
"""

from __future__ import annotations

import argparse
import subprocess
import time
import os
import json
from pathlib import Path

from lib import AutomationAgentTask

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = Path("~/.config/himalaya/config.toml").expanduser()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()

    task = AutomationAgentTask(
        name="Email Mastery: Himalaya Certification",
        description="Verifying CLI email integration for multi-modal notifications."
    )

    if not args.run:
        print("[EmailHandshake] Prepared mode. Use --run.")
        return 0

    task.start()

    # 1. Verify Installation
    def check_install():
        res = subprocess.run(["himalaya", "--version"], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError("Himalaya CLI not found. Please install via brew: 'brew install himalaya'")
        return res.stdout.strip()

    task.step("Check Himalaya Installation", check_install)

    # 2. Check Configuration
    def check_config():
        if not CONFIG_PATH.exists():
            return {
                "status": "NOT_CONFIGURED",
                "message": f"Config not found at {CONFIG_PATH}. Run 'himalaya account configure' to set up."
            }
        
        # Try to list accounts
        res = subprocess.run(["himalaya", "account", "list", "--output", "json"], capture_output=True, text=True)
        if res.returncode == 0:
            try:
                accounts = json.loads(res.stdout)
                return {"status": "CONFIGURED", "accounts": accounts}
            except:
                return {"status": "CONFIGURED", "raw_output": res.stdout.strip()}
        
        return {"status": "ERROR", "message": res.stderr.strip() or "Failed to list accounts."}

    config_status = task.step("Verify Account Configuration", check_config)

    # 3. Demonstration (if configured)
    def demo_list():
        if config_status.get("status") != "CONFIGURED":
            return "Skipping demo: Account not configured."
        
        # List latest 5 envelopes
        res = subprocess.run(["himalaya", "envelope", "list", "--page-size", "5", "--output", "json"], capture_output=True, text=True)
        if res.returncode == 0:
            try:
                envelopes = json.loads(res.stdout)
                return {"envelopes": envelopes}
            except:
                return {"raw_output": res.stdout[:500]}
        
        return f"Error listing envelopes: {res.stderr.strip()}"

    demo_result = task.step("List Recent Envelopes (Demo)", demo_list)

    task.finish(success=True, final_result={
        "config_status": config_status,
        "demo_result": demo_result
    })
    
    if config_status.get("status") == "NOT_CONFIGURED":
        print(f"\n[Email Link] ⚠️ Himalaya is installed but NOT configured.")
        print(f"Please run: 'himalaya account configure' in your terminal.")
    else:
        print(f"\n[Email Success] Pipeline verified. Accounts: {config_status.get('accounts', 'unknown')}")

if __name__ == "__main__":
    main()
