#!/usr/bin/env bash

echo "🛑 Stopping running jarvis backend processes..."
pkill -f "jarvis serve" || true

# Wait a moment for processes to cleanly exit
sleep 2

echo "🚀 Starting OpenJarvis backend server..."
# We start it using the virtual environment python to avoid any path issues
nohup ./.venv/bin/jarvis serve > backend.log 2>&1 &

echo "✅ Backend restarted successfully!"
echo "📄 You can monitor the logs with: tail -f backend.log"
