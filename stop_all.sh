#!/bin/bash
# Stop all services

echo "=========================================="
echo "Stopping All Services"
echo "=========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

stop_service() {
    local service_name=$1
    local service_dir=$2
    
    if [ -f "$service_dir/${service_name}.pid" ]; then
        PID=$(cat "$service_dir/${service_name}.pid")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping $service_name (PID: $PID)..."
            kill $PID
            rm "$service_dir/${service_name}.pid"
            echo "✓ $service_name stopped"
        else
            echo "⚠ $service_name not running"
            rm "$service_dir/${service_name}.pid"
        fi
    else
        echo "⚠ No PID file for $service_name"
    fi
}

stop_service "suggestion" "$SCRIPT_DIR/suggestion"
stop_service "related" "$SCRIPT_DIR/related"
stop_service "multiagent" "$SCRIPT_DIR/multiagent"

# Also kill any processes on these ports (backup)
for port in 8000 8001 8002; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "Killing process on port $port (PID: $PID)"
        kill -9 $PID 2>/dev/null
    fi
done

echo ""
echo "✓ All services stopped"
echo ""