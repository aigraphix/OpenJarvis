import sqlite3
import sys
import os
import json
import time

DB_PATH = os.path.expanduser("~/.gemini/working_memory.db")

def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS state 
                 (key TEXT PRIMARY KEY, value TEXT, updated_at INTEGER, source TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS evidence 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, output TEXT, exit_code INTEGER, ts INTEGER)''')
    conn.commit()
    return conn

def set_state(key, value, source="system"):
    conn = ensure_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO state (key, value, updated_at, source) VALUES (?, ?, ?, ?)",
              (key, str(value), int(time.time()), source))
    conn.commit()
    conn.close()
    print(f"STATE_SET: {key} -> {value}")

def get_state(key):
    conn = ensure_db()
    c = conn.cursor()
    c.execute("SELECT value FROM state WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    if row:
        print(row[0])
    else:
        print(f"ERROR: Key '{key}' not found.")
        sys.exit(1)

def log_evidence(command, output, exit_code):
    conn = ensure_db()
    c = conn.cursor()
    c.execute("INSERT INTO evidence (command, output, exit_code, ts) VALUES (?, ?, ?, ?)",
              (command, output, exit_code, int(time.time())))
    conn.commit()
    conn.close()

def reconcile():
    conn = ensure_db()
    c = conn.cursor()
    c.execute("SELECT value FROM state WHERE key = 'last_checkpoint'")
    row = c.fetchone()
    conn.close()
    if not row:
        print("RECONCILE: No checkpoint found. Safe to start fresh.")
        return

    state = json.loads(row[0])
    ts = state.get("ts", 0)
    diff = int(time.time()) - ts
    
    if diff > 600: # 10 minutes
        print(f"RECONCILE: Stale checkpoint detected ({diff}s old). Recommendation: RE-PLAN.")
        os.system(f"pnpm nexus system event --text 'Reconciliation: Stale state found ({diff}s). Re-planning required.' --mode 'now'")
    else:
        print(f"RECONCILE: Fresh state ({diff}s old). Safe to resume task: {state.get('taskId')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: brain [set|get|evidence|checkpoint|reconcile] ...")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "set" and len(sys.argv) == 4:
        set_state(sys.argv[2], sys.argv[3])
    elif cmd == "get" and len(sys.argv) == 3:
        get_state(sys.argv[2])
    elif cmd == "checkpoint" and len(sys.argv) == 6:
        set_checkpoint(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "reconcile":
        reconcile()
    elif cmd == "evidence":
        # Simplified evidence logging
        pass
    else:
        print("Unknown command or missing arguments.")
