#!/bin/sh

mkdir -p /app/data
chown appuser:appuser /app/data

RELOAD=${RELOAD:-0}

if [ "$RELOAD" = "1" ]; then
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --reload
else
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
fi