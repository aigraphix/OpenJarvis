import os
import time
import subprocess
import sys
import json

# CONFIGURATION
APP_NAME = "Electron"  # Update if the process name changes
CHECK_INTERVAL = 30    # seconds
SCREENSHOT_PATH = "/tmp/antigravity_watchdog.png"
RETRY_SCRIPT = os.path.join(os.path.dirname(__file__), "find_and_retry.applescript")
BEACON_SCRIPT = os.path.join(os.path.dirname(__file__), "presence_beacon.cjs")

def log(message):
    print(f"[Watchdog] {time.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def get_idle_time():
    """Returns system idle time in seconds using ioreg."""
    try:
        cmd = "ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print $NF/1000000000; exit}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return float(result.stdout.strip())
    except:
        return 0

def start_presence_beacon():
    """Starts the Node.js presence beacon to announce our existence to the Gateway."""
    log("Starting presence beacon...")
    try:
        # Launch as a separate process and log its output
        with open("beacon.log", "a") as f:
            subprocess.Popen(["node", BEACON_SCRIPT], stdout=f, stderr=f)
    except Exception as e:
        log(f"Failed to start presence beacon: {e}")

def check_for_error():
    """
    Takes a screenshot and checks for error conditions.
    This is a placeholder for more advanced detection like OCR or pixel analysis.
    For now, we can check if the app is still responsive or use AppleScript to query window state.
    """
    try:
        # Take a screenshot
        subprocess.run(["screencapture", "-x", SCREENSHOT_PATH], check=True)
        # Note: In a real implementation, we could use Pillow to check for 
        # the specific red 'error' banner color at the bottom of the chat.
        return False # Placeholder: returning False to prevent focus stealing until real detection is implemented
    except Exception as e:
        log(f"Error taking screenshot: {e}")
        return False

def trigger_retry(allow_focus=False):
    log(f"Detection triggered. Attempting to click Retry (Allow Focus: {allow_focus})...")
    try:
        # 1. Execute the UI automation
        args = [RETRY_SCRIPT]
        if allow_focus:
            args.append("focus")
        
        result = subprocess.run(args, capture_output=True, text=True)
        log(f"AppleScript Result: {result.stdout.strip()}")
        
        if "Clicked" in result.stdout:
            # 2. Emit a structured system event to the Gateway
            # This allows other agents and the TUI to sync with the recovery.
            event_data = {
                "kind": "antigravity.watchdog.recovery",
                "agentId": "main",
                "detected": "Agent Terminated / Timeout",
                "action": "clicked_retry",
                "ts": int(time.time())
            }
            # 2. Notify the Gateway via RPC call
            subprocess.run([
                "pnpm", "nexus", "gateway", "call", "system-presence",
                "--params", json.dumps({"text": f"Watchdog Recovery: {event_data['detected']}"})
            ])

    except Exception as e:
        log(f"Failed to execute recovery: {e}")

def setup_logging():
    log("--- Watchdog Session Started ---")
    log(f"Architecture: Coordinator (Antigravity) + Orchestrator (Nexus)")
    log(f"Sync: Presence Beacon + System Events enabled")

# --- NEXUS LINK INTEGRATION ---
NEXUS_MAILBOX = "/Users/danny/Desktop/nexus/.agent/nexus_signals.json"

def check_nexus_signals():
    """Polls the Nexus Mailbox for 'WAKE' signals from Nexus."""
    if not os.path.exists(NEXUS_MAILBOX):
        return

    try:
        with open(NEXUS_MAILBOX, "r") as f:
            data = json.load(f)
            
        signal = data.get("antigravity", {})
        if signal.get("status") == "WAKE":
            msg = signal.get("message", "No message provided.")
            sender = signal.get("sender", "Unknown Agent")
            is_unattended = "#unattended" in msg.lower() or signal.get("mode") == "unattended"
            
            log(f"🚨 NEXUS WAKE DETECTED from {sender} (Mode: {'Unattended' if is_unattended else 'Interactive'})")
            
            if is_unattended:
                # 1. Shadow Proxy Mode (Bypass Popup)
                log("Executing in Unattended Mode...")
                subprocess.run(["say", f"Nexus Wake. Executing unattended request from {sender}."])
                # 1. Interactive Mode - Use NOTIFICATION instead of ALERT to avoid focus stealing
                subprocess.run(["say", f"Attention. Nexus Wake from {sender}."])
                # We use 'display notification' which does not steal focus
                notify_script = f'display notification "{msg}" with title "Nexus Wake: {sender}"'
                subprocess.run(["osascript", "-e", notify_script])
            
            log(f"✅ Mission Acknowledged (Agent Proxy: {'Watchdog' if is_unattended else 'Human'}).")

            # 2. Update Mailbox with Handshake
            signal["status"] = "ACKNOWLEDGED"
            signal["acknowledged_at"] = time.time()
            signal["proxy_type"] = "Shadow" if is_unattended else "Human"
            with open(NEXUS_MAILBOX, "w") as f:
                json.dump(data, f, indent=2)
            
            # 3. Notify Nexus (The Bridge)
            report_msg = f"🤝 NEXUS HANDSHAKE COMPLETE: Handled via {signal['proxy_type']} Proxy. Executing: {msg}"
            subprocess.run([
                "pnpm", "nexus", "agent", 
                "--agent", "main", 
                "--message", report_msg, 
                "--deliver"
            ], capture_output=True)

            # 4. Take "Proof of Work" Screenshot (Optional but helpful for remote)
            if is_unattended:
                ts = int(time.time())
                ss_path = f"/tmp/nexus_proof_{ts}.png"
                subprocess.run(["screencapture", "-x", ss_path])
                log(f"Proof of Work captured at {ss_path}")

            # 5. Bring IDE to front ONLY if inactive for > 60s
            idle = get_idle_time()
            if idle > 60:
                log(f"Inactivity detected ({idle:.1f}s). Bringing IDE to front.")
                subprocess.run(["osascript", "-e", f'tell application "System Events" to set frontmost of process "{APP_NAME}" to true'])
            else:
                log(f"User active ({idle:.1f}s). Keeping IDE in background.")

    except Exception as e:
        log(f"Nexus Signal check failed: {e}")

def main():
    setup_logging()
    log(f"Starting Antigravity Watchdog (Nexus-Link Enabled)")
    start_presence_beacon()
    try:
        while True:
            # Check for Inter-Agent Signals (Nexus Link)
            check_nexus_signals()

            # Check for the app state (IDE health)
            check_app = subprocess.run(["osascript", "-e", f'tell application "System Events" to exists process "{APP_NAME}"'], capture_output=True, text=True)
            
            if "true" in check_app.stdout.lower():
                if check_for_error():
                    idle = get_idle_time()
                    trigger_retry(allow_focus=(idle > 60))
            else:
                log(f"Idle: {APP_NAME} not found. Assistant might be sleeping.")
                
            sys.stdout.flush() 
            time.sleep(10) # Faster poll for better 'Wake' responsiveness
    except KeyboardInterrupt:
        log("Watchdog stopped by user.")

if __name__ == "__main__":
    main()
