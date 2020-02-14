#!/bin/bash
set -e

if (($#)); then
    exec "$@"
else
    gunicorn application.wsgi:application \
        --worker-connections="$WORKER_CONNECTIONS" \
        --workers="$WORKERS" \
        --bind 0.0.0.0:8000
fi

