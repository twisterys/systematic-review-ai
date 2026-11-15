#!/usr/bin/env bash
# Quick launcher for Streamlit Web Application

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Use virtualenv if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "🚀 Starting Multi-Agent Systematic Review Web Dashboard..."
streamlit run app.py
