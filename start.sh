#!/bin/bash

# This starts your FastAPI app using Gunicorn + UvicornWorker
# on the correct host and port Render expects

gunicorn main:app \
    --workers 3 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:9000 \
    --timeout 180
