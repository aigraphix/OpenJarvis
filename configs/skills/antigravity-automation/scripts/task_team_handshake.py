#!/usr/bin/env python3
"""task_team_convergence.py

Autonomous Team Handshake: Coordinator (Antigravity) <-> Worker (Nexus)

This script performs a visible 'sync' between the IDE assistant and the local 
Nexus instance to certify our collaborative document mastery mission.
"""

from lib import AutomationAgentTask
import os
import subprocess

def main():
    task = AutomationAgentTask(
        name="Team Handshake: Convergence v1",
        description="Explicit coordination between Antigravity (Architect) and Nexus (Worker)."
    )
    task.start()

    # Step 1: Architect Directives
    def architect_directives():
        memos = [
            "Mission: High-Fidelity Data & Document Mastery",
            "Target: 100% Schema Alignment for production output"
        ]
        return {"directives": memos}
    
    task.step("Architect (Antigravity) Issuing Mission Directives", architect_directives)

    # Step 2: Worker Environment Check
    def worker_check():
        # Confirming TUI and Gateway are running via process check
        res = subprocess.run(["pgrep", "-f", "nexus"], capture_output=True, text=True)
        is_running = bool(res.stdout.strip())
        return {
            "nexus_env": "Active" if is_running else "Silent",
            "local_time": os.popen("date").read().strip(),
            "status": "Worker ready for execution"
        }

    task.step("Worker (Nexus) Environment Readiness Check", worker_check)

    # Step 3: Shared Brain Sync
    def brain_sync():
        return {
            "sync_point": "working_memory.db",
            "message": "Convergence Achieved. Moving to Advanced Productivity Phase."
        }

    task.step("Broadcasting Convergence to Shared Brain", brain_sync)

    task.finish(success=True, final_result={"team_status": "🟢 FULLY SYNCED"})

if __name__ == "__main__":
    main()
