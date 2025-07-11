#!/bin/bash

# Use Render-provided PORT or default to 10000 for local testing
PORT=${PORT:-10000}

echo "📦 Starting Gunicorn server on port $PORT..."

gunicorn main:app \
    --workers 3 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 180
