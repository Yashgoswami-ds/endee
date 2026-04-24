#!/bin/bash

# Setup script for AI Knowledge Assistant (Linux/Mac)

echo ""
echo "================================"
echo "AI Knowledge Assistant Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "[1] Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[2] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[3] Installing dependencies..."
pip install -r requirements.txt --quiet

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "[4] Creating .env configuration file..."
    cat > .env << EOF
ENDEE_BASE_URL=https://api.endee.ai/v1
ENDEE_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=False
EOF
    echo "[!] .env created - UPDATE with your Endee API key"
fi

# Create data directories
if [ ! -d "data/uploads" ]; then
    echo "[5] Creating data directories..."
    mkdir -p data/uploads
fi

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Endee API key"
echo "2. Run: python3 app.py"
echo "3. Open http://127.0.0.1:5000 in your browser"
echo ""
