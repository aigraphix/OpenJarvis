#!/usr/bin/osascript

on run argv
    set appName to "Electron"
    set resumePrompt to "Please continue exactly where you left off."
    
    tell application "System Events"
        if exists process appName then
            tell process appName
                set frontmost to true
                delay 1 -- wait for focus
                
                -- Simulate typing the prompt and hitting enter
                -- This assumes the chat focus is in the right place
                keystroke resumePrompt
                keystroke return
                return "Sent resume prompt: " & resumePrompt
            end tell
        else
            return "Error: Process " & appName & " not found."
        end if
    end tell
end run
