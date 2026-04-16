import os
import subprocess
import time
import argparse
import json
from lib import AutomationAgentTask

def get_icon_positions_sample(sample_n: int = 3):
    """Return a small sample of desktop icon positions.

    Evidence-first goal: prove the Desktop *reacted* without journaling every icon.

    Returns:
      List[dict]: [{"name": str, "x": int, "y": int}]

    Notes:
    - Samples the first N items sorted by name for determinism.
    - Uses Finder's `desktop position` (icon view). If unavailable, returns [].
    """
    script = f'''
    tell application "Finder"
        set itemsList to every item of desktop
        set nameList to {{}}
        repeat with i in itemsList
            set end of nameList to (name of i)
        end repeat
        set nameList to my sort_list(nameList)

        set outLines to {{}}
        set n to {int(sample_n)}
        if n < 1 then set n to 1

        repeat with idx from 1 to (count of nameList)
            if idx > n then exit repeat
            set nm to item idx of nameList
            set it to (first item of desktop whose name is nm)
            set p to (desktop position of it)
            set x to item 1 of p
            set y to item 2 of p
            set end of outLines to (nm & "|" & x & "|" & y)
        end repeat
        return outLines
    end tell

    on sort_list(theList)
        set theIndex to 1
        repeat while theIndex < (count theList)
            set theIndex2 to theIndex + 1
            repeat while theIndex2 ≤ (count theList)
                if (item theIndex2 of theList) < (item theIndex of theList) then
                    set theTemp to item theIndex of theList
                    set item theIndex of theList to item theIndex2 of theList
                    set item theIndex2 of theList to theTemp
                end if
                set theIndex2 to theIndex2 + 1
            end repeat
            set theIndex to theIndex + 1
        end repeat
        return theList
    end sort_list
    '''

    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        return []

    lines = [ln.strip() for ln in (result.stdout or "").split(",")]
    # osascript returns AppleScript list with commas; be defensive.
    parsed = []
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        parts = raw.split("|")
        if len(parts) != 3:
            continue
        name, x, y = parts
        try:
            parsed.append({"name": name, "x": int(float(x)), "y": int(float(y))})
        except Exception:
            continue
    return parsed

def trigger_hybrid_cleanup():
    """
    Hybrid v8: Combines UI visibility with native menu precision.
    """
    script = '''
    -- Step 1: Show Desktop (Clear the workspace)
    tell application "System Events"
        key code 160 using {command down}
        delay 2
    end tell

    -- Step 2: Trigger the native 'Clean Up By Name' menu command
    tell application "Finder"
        activate
    end tell

    tell application "System Events"
        tell process "Finder"
            try
                click menu item "Name" of menu 1 of menu item "Clean Up By" of menu 1 of menu bar item "View" of menu bar 1
                delay 1
            on error err
                return "Error: " & err
            end try
        end tell
    end tell
    
    tell application "Finder" to update desktop
    return "Hybrid v8 Cleanup Protocol Executed"
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"AppleScript Trace: {result.stderr}")
    
    if "Error:" in result.stdout:
        raise Exception(f"UI Scripting Error: {result.stdout.strip()}")
        
    return result.stdout.strip()

def cleanup_desktop(should_run=False):
    task = AutomationAgentTask(
        name="Desktop Clean Up (Canonical v8)",
        description="Hybrid protocol with post-condition verification."
    )
    
    if not should_run:
        print("[AutomationAgent] Script staged in 'Prepared' mode. Use --run to execute.")
        return

    task.start()
    
    try:
        # Step 0: Pre-check (sample 3 positions)
        pre_sample = task.step(
            "Pre-Cleanup Verification (Sample 3)",
            get_icon_positions_sample,
            3,
        )
        
        # Step 1: Execute the Hybrid UI sequence
        result = task.step("Trigger Hybrid UI Protocol", trigger_hybrid_cleanup)
        
        # Step 2: Post-check (sample 3 positions)
        time.sleep(1)  # Allow Finder animation
        post_sample = task.step(
            "Post-Cleanup Verification (Sample 3)",
            get_icon_positions_sample,
            3,
        )

        # Determine if anything moved (by name)
        pre_map = {i.get("name"): (i.get("x"), i.get("y")) for i in (pre_sample or [])}
        post_map = {i.get("name"): (i.get("x"), i.get("y")) for i in (post_sample or [])}
        moved_count = 0
        for name, pos in pre_map.items():
            if name in post_map and post_map[name] != pos:
                moved_count += 1
        
        final_result = {
            "status": "Success",
            "pre_sample": pre_sample,
            "post_sample": post_sample,
            "moved_count": moved_count,
            "verification": "Change detected" if moved_count > 0 else "No change detected (could be already sorted or UI action did not apply)",
        }
        
        task.finish(success=True, final_result=final_result)
        print(f"[AutomationAgent] Cleanup Complete. Moved {moved_count} items.")

    except Exception as e:
        task.finish(success=False, final_result={"error": str(e)})
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Actually execute the cleanup protocol")
    args = parser.parse_args()
    
    cleanup_desktop(should_run=args.run)
