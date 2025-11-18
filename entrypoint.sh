#!/bin/bash
case ${SERVICE:-suggestion} in
  suggestion)
    cd /app/suggestion
    . venv/bin/activate
    exec uvicorn app:app --host 0.0.0.0 --port 8000
    ;;
  related)
    cd /app/related
    . venv/bin/activate
    exec uvicorn app:app --host 0.0.0.0 --port 8001
    ;;
  multiagent)
    cd /app/multiagent
    . venv/bin/activate
    exec uvicorn app:app --host 0.0.0.0 --port 8002
    ;;
  *)
    echo "Unknown service: $SERVICE"
    exit 1
    ;;
esac
