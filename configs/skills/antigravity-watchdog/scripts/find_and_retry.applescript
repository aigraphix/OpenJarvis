#!/usr/bin/osascript

on run argv
    set appName to "Electron" -- Current best guess for Antigravity process name
    set buttonName to "Retry"  -- The text on the button
    set shouldFocus to false
    if (count of argv) > 0 then
        if item 1 of argv is "focus" then
            set shouldFocus to true
        end if
    end if
    
    tell application "System Events"
        if exists process appName then
            tell process appName
                if shouldFocus then
                    set frontmost to true
                end if
                try
                    -- Try to find the button by name first (Accessibility)
                    set targetButton to (first button whose name contains buttonName) of window 1
                    click targetButton
                    return "Clicked button: " & buttonName
                on error
                    -- Fallback: If accessibility fails or name is different, report back
                    return "Error: Could not find button named " & buttonName
                end try
            end tell
        else
            return "Error: Process " & appName & " not found."
        end if
    end tell
end run
