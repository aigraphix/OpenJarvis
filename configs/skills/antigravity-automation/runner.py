import os
import sys
import subprocess
from pathlib import Path
from lib import AutomationAgentTask

# CONFIGURATION
AUTOMATION_ROOT = Path(__file__).parent
SCRIPTS_DIR = AUTOMATION_ROOT / "scripts"

def run_automation(script_name, args):
    """Runs a Python script within the Automation Agent framework."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"Error: Script {script_name} not found.")
        return 1

    # We use sys.executable to ensure we use the same environment
    print(f"[Runner] Launching {script_name}...")
    
    # We pass the sys.path to the subprocess so it can find lib.py
    env = os.environ.copy()
    env["PYTHONPATH"] = str(AUTOMATION_ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    result = subprocess.run(
        [sys.executable, str(script_path)] + args,
        env=env
    )
    
    return result.returncode

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 runner.py <script_name> [args...]")
        sys.exit(1)
    
    sys.exit(run_automation(sys.argv[1], sys.argv[2:]))
