#!/usr/bin/env bash

set -eux

# Install python requirements
pip install -r requirements.txt

# Generate environment
python scripts/generate_env_override.py
python scripts/generate_env.py

docker compose up -d

mkdir -p logs

# Initialize minio
python scripts/initialize_minio.py

# Initialize django
python manage.py collectstatic --noinput -v 3
python manage.py migrate

# Load test data
# TODO: build proper test data
python manage.py loaddata fixtures/*

echo "Done initialising TQ website."
