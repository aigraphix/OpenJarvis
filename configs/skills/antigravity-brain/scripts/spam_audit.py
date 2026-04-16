import sqlite3
import json
import time
import os
import subprocess

DB_PATH = os.path.expanduser("~/.gemini/working_memory.db")

def ensure_spam_tables():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS spam_candidates 
                 (message_id TEXT PRIMARY KEY, thread_id TEXT, subject TEXT, sender TEXT, 
                  label TEXT, status TEXT, discovered_at INTEGER)''')
    conn.commit()
    conn.close()

def ingest_candidates(label="spam"):
    """Runs gog search and stores metadata in the brain."""
    ensure_spam_tables()
    print(f"INGEST: Searching for '{label}'...")
    
    # Run gog search with JSON output
    # Note: We expect 'gog' to be authenticated by the user first.
    try:
        # We'll use a placeholder search for now until gog is authenticated
        # In a real run, this would be: 
        # result = subprocess.run(["gog", "gmail", "search", f"label:{label}", "--json"], capture_output=True, text=True)
        # messages = json.loads(result.stdout)
        
        # MOCK DATA for testing the 'Team Convergence'
        messages = [
            {"id": "msg_123", "threadId": "thr_abc", "subject": "Free Prize!", "from": "spam@example.com"},
            {"id": "msg_456", "threadId": "thr_def", "subject": "Urgent: Account Update", "from": "hacker@malware.com"}
        ]
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        for m in messages:
            c.execute("INSERT OR IGNORE INTO spam_candidates VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (m['id'], m['threadId'], m.get('subject', ''), m.get('from', ''), label, 'pending_review', int(time.time())))
        conn.commit()
        conn.close()
        print(f"INGEST: Added {len(messages)} candidates to the Brain.")
    except Exception as e:
        print(f"INGEST_ERROR: {e}")

def summarize_candidates():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT label, COUNT(*) FROM spam_candidates WHERE status = 'pending_review' GROUP BY label")
    rows = c.fetchall()
    conn.close()

    summary = {r[0]: r[1] for r in rows}
    print(f"SUMMARY: {json.dumps(summary)}")
    return summary


def rescue_candidate(message_id: str):
    """Marks a candidate as rescued (moved to Inbox / not spam) by message_id."""
    ensure_spam_tables()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(
        "UPDATE spam_candidates SET status = 'rescued' WHERE message_id = ?",
        (message_id,),
    )
    updated = c.rowcount
    conn.commit()
    conn.close()

    if updated == 0:
        print(f"RESCUE: message_id not found: {message_id}")
        return False

    print(f"RESCUE: marked message_id as rescued: {message_id}")
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: spam_audit.py [ingest|summary|rescue <message_id>]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "ingest":
        ingest_candidates()
    elif cmd == "summary":
        summarize_candidates()
    elif cmd == "rescue":
        if len(sys.argv) < 3:
            print("Usage: spam_audit.py rescue <message_id>")
            sys.exit(1)
        rescue_candidate(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: spam_audit.py [ingest|summary|rescue <message_id>]")
        sys.exit(1)
