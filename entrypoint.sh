#!/bin/bash
set -e

case ${SERVICE:-suggestion} in
  suggestion)
    cd /app/suggestion
    exec uvicorn app:app --host 0.0.0.0 --port 8000
    ;;
  related)
    cd /app/related
    exec uvicorn app:app --host 0.0.0.0 --port 8001
    ;;
  multiagent)
    cd /app/multiagent
    exec uvicorn app:app --host 0.0.0.0 --port 8002
    ;;
  *)
    echo "Unknown service: $SERVICE"
    exit 1
    ;;
esac
