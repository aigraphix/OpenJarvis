import os
import sqlite3
import time
import json
import subprocess
from pathlib import Path

# SHARED CONFIGURATION
# Brain DB location (project-local preferred for portability / Mission Control)
# Priority:
# 1) env AUTOMATION_AGENT_BRAIN_DB
# 2) <repo-root>/.agent/working_memory.db
# 3) ~/.gemini/working_memory.db (legacy fallback)

def _resolve_brain_db() -> str:
    env = (os.environ.get("AUTOMATION_AGENT_BRAIN_DB") or "").strip()
    if env:
        return os.path.expanduser(env)

    repo_root = Path(__file__).resolve().parents[2]
    memory_db = repo_root / "memory" / "working_memory.db"
    if memory_db.exists():
        return str(memory_db)

    return os.path.expanduser("~/.gemini/working_memory.db")


BRAIN_DB = _resolve_brain_db()

class AutomationAgentTask:
    """An Automation Agent task wrapper for Python automation."""
    
    def __init__(self, name, description="No description provided"):
        self.name = name
        self.description = description
        self.start_time = time.time()
        self.steps = []
        self._initialize_brain()

    def _initialize_brain(self):
        """Ensure the automation tables exist in the brain."""
        conn = sqlite3.connect(BRAIN_DB)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                status TEXT,
                started_at INTEGER,
                finished_at INTEGER,
                result TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                step_name TEXT,
                status TEXT,
                output TEXT,
                ts INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def step(self, name, func, *args, **kwargs):
        """Executes a single step in the task."""
        print(f"[AutomationAgent] Step: {name}...")
        ts = int(time.time())
        try:
            output = func(*args, **kwargs)
            status = "SUCCESS"
            print(f"[AutomationAgent] Step '{name}' completed successfully.")
        except Exception as e:
            output = str(e)
            status = "FAILED"
            print(f"[AutomationAgent] Step '{name}' FAILED: {output}")
        
        self.steps.append({
            "name": name,
            "status": status,
            "output": output,
            "ts": ts
        })
        
        # Log to Brain immediately (incremental progress)
        self._log_step(name, status, str(output), ts)
        
        if status == "FAILED":
            raise Exception(f"Task aborted at step '{name}': {output}")
        
        return output

    def _log_step(self, step_name, status, output, ts):
        conn = sqlite3.connect(BRAIN_DB)
        cursor = conn.cursor()
        # Find the latest task ID for this name that started recently
        cursor.execute("SELECT id FROM automation_tasks WHERE name = ? ORDER BY started_at DESC LIMIT 1", (self.name,))
        task_row = cursor.fetchone()
        if task_row:
            task_id = task_row[0]
            cursor.execute(
                "INSERT INTO automation_steps (task_id, step_name, status, output, ts) VALUES (?, ?, ?, ?, ?)",
                (task_id, step_name, status, output, ts)
            )
        conn.commit()
        conn.close()

    def start(self, max_retries=5, priority=0):
        print(f"[AutomationAgent] Task Started: {self.name} - {self.description}")
        conn = sqlite3.connect(BRAIN_DB)
        cursor = conn.cursor()
        
        # Check if task already exists in BACKLOG or FAIL_RETRY
        cursor.execute("SELECT id, retry_count FROM automation_tasks WHERE name = ? AND status IN ('BACKLOG', 'FAIL_RETRY') ORDER BY id DESC LIMIT 1", (self.name,))
        existing = cursor.fetchone()
        
        if existing:
            task_id, retry_count = existing
            cursor.execute(
                "UPDATE automation_tasks SET status = 'RUNNING', started_at = ?, max_retries = ?, priority = ? WHERE id = ?",
                (int(self.start_time), max_retries, priority, task_id)
            )
        else:
            cursor.execute(
                "INSERT INTO automation_tasks (name, description, status, started_at, max_retries, priority) VALUES (?, ?, ?, ?, ?, ?)",
                (self.name, self.description, "RUNNING", int(self.start_time), max_retries, priority)
            )
        
        conn.commit()
        conn.close()
        # Emit system event (simplified as a shell command for now)
        event_msg = f"Task Started: {self.name}"
        subprocess.run(["nexus", "gateway", "wake", "--message", f"Automation Agent: {event_msg}"], capture_output=True)

    def finish(self, success=True, final_result=None, terminal_reason=None):
        finished_at = int(time.time())
        conn = sqlite3.connect(BRAIN_DB)
        cursor = conn.cursor()
        
        # Get current state
        cursor.execute("SELECT id, retry_count, max_retries FROM automation_tasks WHERE name = ? AND status = 'RUNNING' ORDER BY id DESC LIMIT 1", (self.name,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return

        task_id, retry_count, max_retries = row
        
        if success:
            status = "SUCCESS"
            cursor.execute(
                "UPDATE automation_tasks SET status = ?, finished_at = ?, result = ? WHERE id = ?",
                (status, finished_at, json.dumps(final_result), task_id)
            )
        else:
            if retry_count < max_retries:
                status = "FAIL_RETRY"
                # Exponential backoff: 30s, 60s, 120s, 240s...
                wait_sec = 30 * (2 ** retry_count)
                next_retry = finished_at + wait_sec
                cursor.execute(
                    "UPDATE automation_tasks SET status = ?, retry_count = ?, next_retry_at = ?, result = ? WHERE id = ?",
                    (status, retry_count + 1, next_retry, json.dumps(final_result), task_id)
                )
            else:
                status = "FAIL_TERMINAL"
                cursor.execute(
                    "UPDATE automation_tasks SET status = ?, finished_at = ?, terminal_reason = ?, result = ? WHERE id = ?",
                    (status, finished_at, terminal_reason or "MAX_RETRIES_EXCEEDED", json.dumps(final_result), task_id)
                )

        conn.commit()
        conn.close()
        
        print(f"[AutomationAgent] Task Finished: {self.name} ({status})")
        event_msg = f"Task {status}: {self.name}"
        subprocess.run(["nexus", "gateway", "wake", "--message", f"Automation Agent: {event_msg}"], capture_output=True)
