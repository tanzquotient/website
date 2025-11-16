#!/bin/sh
set -e  # exit on error

# 1) Run pre-start scripts
/app/scripts/generate_env_sip.sh
/app/scripts/pre-start.sh

# 3) Start background stuff
/app/scripts/post-start.sh &
celery --app=tq_website worker --loglevel=info &
celery --app=tq_website beat --loglevel=info --scheduler=django &

# 3) Start the main process
exec gunicorn --bind=0.0.0.0:8080 --workers=4 --timeout=30 tq_website.wsgi:application



