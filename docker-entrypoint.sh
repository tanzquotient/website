#!/bin/sh
set -e  # exit on error

# set prometheus_client's multiprocess directory
export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus-multiproc

# 1) Run pre-start scripts
/app/scripts/generate_env_sip.sh
/app/scripts/pre-start.sh

# 3) Start background stuff
/app/scripts/post-start.sh &
nice -n 10 celery --app=tq_website worker --loglevel=info \
  --concurrency=1 \
  --max-tasks-per-child=100 \
  --max-memory-per-child=512000 \
  --time-limit=1800 --soft-time-limit=1500 &
nice -n 10 celery --app=tq_website beat --loglevel=info --scheduler=django &

# 3) Start the main process
exec gunicorn --bind=0.0.0.0:8080 --workers=4 --timeout=30 \
  --max-requests=1000 --max-requests-jitter=100 \
  --config /app/gunicorn.conf.py \
  tq_website.wsgi:application



