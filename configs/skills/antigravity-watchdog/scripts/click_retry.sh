#!/bin/bash
# click_retry.sh
# Usage: ./click_retry.sh <X_COORD> <Y_COORD>

osascript <<EOD
tell application "System Events"
    tell process "Electron"
        set frontmost to true
        click at {$1, $2}
    end tell
end tell
EOD
