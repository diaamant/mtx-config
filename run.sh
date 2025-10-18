#!/bin/bash
# Quick start script for Mediamtx Configuration Editor

set -e

echo "🚀 Starting Mediamtx Configuration Editor..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv .venv && source .venv/bin/activate && pip install uv && uv pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import nicegui" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install uv
    uv pip install -r requirements.txt
fi

# Run the application
echo "🌐 Starting application on http://localhost:8080"
echo "Press Ctrl+C to stop"
echo ""
python3 src/main.py
