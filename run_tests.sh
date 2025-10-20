#!/bin/bash
# Script to run Playwright tests for mtx-config

set -e

echo "🚀 Starting Playwright tests for mtx-config..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: source .venv/bin/activate && uv pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Start the application in background
echo "🌐 Starting application..."
PYTHONPATH=/mnt/data/storeSoft/projPySample/mtx-config/src python -m src.main &
APP_PID=$!

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 3

# Run Playwright tests
echo "🧪 Running Playwright tests..."
python -m pytest tests/test_filters.py -v -m playwright

# Stop the application
echo "🛑 Stopping application..."
kill $APP_PID 2>/dev/null || true

echo "✅ Tests completed!"
