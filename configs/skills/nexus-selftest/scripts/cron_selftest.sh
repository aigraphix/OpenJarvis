#!/bin/bash
# Nexus Scheduled Self-Test Runner
# Runs daily at 6:00 AM and emails failures to the configured address

# Configuration
EMAIL="apd1034@gmail.com"
NEXUS_ROOT="/Users/danny/Desktop/nexus"
PYTHON="python3"

# Change to Nexus root
cd "$NEXUS_ROOT" || exit 1

# Run scheduled self-test with email notifications
$PYTHON skills/nexus-selftest/scripts/scheduled_test.py --email "$EMAIL" --local

# Log completion
echo "[$(date)] Self-test completed with exit code: $?" >> "$NEXUS_ROOT/workspace/selftest/cron.log"
