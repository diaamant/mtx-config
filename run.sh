#!/bin/bash
# Quick start script for Mediamtx Configuration Editor

set -e

echo "🚀 Starting Mediamtx Configuration Editor..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please install uv virtual environment: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Please run: source $HOME/.cargo/env"
    echo "Activate the virtual environment: source .venv/bin/activate"
    echo "Install requirements: uv pip sync requirements.txt --link-mode=copy"
    exit 1
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import nicegui" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    uv pip install -r requirements.txt
fi

# Run the application
echo "🌐 Starting application on http://localhost:8080"
echo "Press Ctrl+C to stop"
echo ""
python3 src/main.py
