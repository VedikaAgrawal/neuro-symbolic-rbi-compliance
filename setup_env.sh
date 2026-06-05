#!/bin/bash
# Setup script for Hybrid Neuro-Symbolic Compliance Guardrails Python environment.

echo "==============================================="
echo "⚙️ Creating fresh Python Virtual Environment..."
echo "==============================================="

# 1. Create virtual environment
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to create virtual environment. Ensure python3 is installed."
    exit 1
fi

echo "✅ Virtual environment 'venv' created successfully."

# 2. Upgrade pip and install dependencies
echo "==============================================="
echo "📦 Installing backend requirements..."
echo "==============================================="
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r backend/requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install Python dependencies."
    exit 1
fi

echo "==============================================="
echo "🎉 Setup Complete!"
echo "==============================================="
echo "To run the FastAPI backend, execute:"
echo "  ./venv/bin/uvicorn backend.main:app --reload --port 8000"
echo ""
echo "To run the React frontend, execute (in a separate terminal):"
echo "  npm run dev"
echo "==============================================="
