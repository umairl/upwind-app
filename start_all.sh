#!/bin/bash
# MLOps Application - Automated Start Script

echo "=========================================="
echo "MLOps Application - Starting Services"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "Setting up and starting services..."
echo ""

# Function to setup and start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3

    echo "----------------------------------------"
    echo "Setting up $service_name (port $port)"
    echo "----------------------------------------"

    cd "$service_dir"

    # Create venv if needed
    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate and install
    echo "  Installing dependencies..."
    source venv/bin/activate
    python -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "  ✗ Failed to install dependencies for $service_name"
        deactivate
        cd "$SCRIPT_DIR"
        return 1
    fi

    # Load config
    if [ -f "config.env" ]; then
        export $(grep -v '^#' config.env | grep -v '^$' | xargs)
    fi

    # Start service in background
    echo "  Starting $service_name..."
    nohup python app.py > "${service_name}.log" 2>&1 &
    echo $! > "${service_name}.pid"

    echo "  ✓ $service_name started (PID: $(cat ${service_name}.pid))"

    deactivate
    cd "$SCRIPT_DIR"
    sleep 2
    return 0
}

# Start all services
start_service "suggestion" "$SCRIPT_DIR/suggestion" 8000
SUGG_STATUS=$?

start_service "related" "$SCRIPT_DIR/related" 8001
REL_STATUS=$?

start_service "multiagent" "$SCRIPT_DIR/multiagent" 8002
MULTI_STATUS=$?

echo ""
echo "=========================================="
echo "Startup Summary"
echo "=========================================="
echo ""

if [ $SUGG_STATUS -eq 0 ]; then
    echo "✓ Suggestion Service:  http://localhost:8000"
else
    echo "✗ Suggestion Service:  FAILED"
fi

if [ $REL_STATUS -eq 0 ]; then
    echo "✓ Related Service:     http://localhost:8001"
else
    echo "✗ Related Service:     FAILED"
fi

if [ $MULTI_STATUS -eq 0 ]; then
    echo "✓ Multiagent Service:  http://localhost:8002"
else
    echo "✗ Multiagent Service:  FAILED"
fi

echo ""
echo "Wait 15-20 seconds for services to fully start"
echo "Then test with: curl http://localhost:8000/health"
echo ""
echo "View logs:"
echo "  tail -f suggestion/suggestion.log"
echo "  tail -f related/related.log"
echo "  tail -f multiagent/multiagent.log"
echo ""
echo "To stop services: ./stop_all.sh"
echo ""