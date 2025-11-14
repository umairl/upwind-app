#!/bin/bash
# MLOps Application - Linux Start Script
# Starts all 3 services in separate terminal tabs/windows

echo "=========================================="
echo "MLOps Application - Starting Services"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install with: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

echo "Starting services..."
echo ""

# Function to start a service in background
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    
    echo "Starting $service_name on port $port..."
    
    cd "$service_dir"
    
    # Create venv if needed
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate and start
    source venv/bin/activate
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Load config
    if [ -f "config.env" ]; then
        export $(grep -v '^#' config.env | grep -v '^$' | xargs)
    fi
    
    # Start service in background
    nohup python app.py > "${service_name}.log" 2>&1 &
    echo $! > "${service_name}.pid"
    
    echo "✓ $service_name started (PID: $(cat ${service_name}.pid))"
    
    cd "$SCRIPT_DIR"
    sleep 2
}

# Start all services
start_service "suggestion" "$SCRIPT_DIR/suggestion" 8000
start_service "related" "$SCRIPT_DIR/related" 8001
start_service "multiagent" "$SCRIPT_DIR/multiagent" 8002

echo ""
echo "=========================================="
echo "All services are starting..."
echo "=========================================="
echo ""
echo "Service URLs:"
echo "  • Suggestion:  http://localhost:8000"
echo "  • Related:     http://localhost:8001"
echo "  • Multiagent:  http://localhost:8002"
echo ""
echo "Wait 15-20 seconds for services to fully start"
echo "Then test with: curl http://localhost:8000/health"
echo ""
echo "Logs are in each service directory:"
echo "  - suggestion/suggestion.log"
echo "  - related/related.log"
echo "  - multiagent/multiagent.log"
echo ""
echo "To stop services, run: ./stop_all.sh"
echo ""