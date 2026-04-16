import os
import time
from pathlib import Path
from lib import AutomationAgentTask

def cleanup_logs():
    task = AutomationAgentTask(
        name="Log Cleanup",
        description="Archives old automation logs into a history folder."
    )
    
    task.start()
    
    try:
        # Define paths
        automation_root = Path(__file__).parent.parent
        logs_dir = automation_root / "logs"
        history_dir = logs_dir / "history"

        # Step 1: Create history dir
        def ensure_dir():
            history_dir.mkdir(exist_ok=True)
            return str(history_dir)
        
        task.step("Ensure History Directory", ensure_dir)

        # Step 2: identify old logs
        def get_old_logs():
            old_logs = []
            now = time.time()
            for log_file in logs_dir.glob("*.log"):
                if now - log_file.stat().st_mtime > 3600: # 1 hour
                    old_logs.append(log_file)
            return [str(f) for f in old_logs]

        old_files = task.step("Identify Stale Logs", get_old_logs)

        # Step 3: Move files
        def archive_files(files):
            count = 0
            for f_path in files:
                p = Path(f_path)
                p.rename(history_dir / p.name)
                count += 1
            return f"Moved {count} files"

        result = task.step("Archive Files", archive_files, old_files)
        
        task.finish(success=True, final_result={"files_moved": len(old_files)})

    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise e

if __name__ == "__main__":
    cleanup_logs()
