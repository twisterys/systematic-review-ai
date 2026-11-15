#!/usr/bin/env bash
# Quick launcher for Streamlit Web Application

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Use virtualenv if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if streamlit is installed
if ! command -v streamlit >/dev/null 2>&1; then
    echo "❌ Streamlit is not installed in your environment."
    echo "💡 Run the following command to install all project dependencies:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

echo "🚀 Starting Multi-Agent Systematic Review Web Dashboard..."
streamlit run app.py
