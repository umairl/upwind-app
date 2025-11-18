#!/bin/bash
set -e

SERVICE=${SERVICE:-suggestion}

cd /app/$SERVICE

# Auto-detect correct Python module file (app.py or main.py or anything else)
if [ -f app.py ]; then
    MODULE="app"
elif [ -f main.py ]; then
    MODULE="main"
else
    echo "ERROR: Could not find app.py or main.py in /app/$SERVICE"
    ls -la
    exit 1
fi

echo "Starting service: $SERVICE (using $MODULE.py)"
exec uvicorn ${MODULE}:app --host 0.0.0.0 --port ${PORT:-8000}
