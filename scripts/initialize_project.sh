#!/usr/bin/env bash

set -eux

# Install python and dependencies, including dev dependencies
uv sync --dev

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

echo "Done initialising TQ website."
