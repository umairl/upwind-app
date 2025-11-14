#!/bin/bash
# Start Multiagent Service

echo "=========================================="
echo "Starting Multiagent Service"
echo "=========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Load environment variables from config.env
echo "Loading configuration..."
if [ -f "config.env" ]; then
    export $(grep -v '^#' config.env | grep -v '^$' | xargs)
fi

# Start the service
echo ""
echo "Multiagent Service starting on port 8002..."
echo "Press Ctrl+C to stop the service"
echo ""

python app.py