#!/usr/bin/env bash

set -eux

# Install python requirements
pip install -r requirements.txt

# Generate environment
python scripts/generate_env_override.py
python scripts/generate_env.py

# Workaround for local minio development
#
# The problem is that "localhost" is not a valid value from the perspective
# of the Django container accessing Minio, and "tq-data" is not a valid value
# from the perspective of your browser accessing Minio.
docker compose up -d

echo "Setting IPs for Minio..."
ip=$(docker inspect tq-data | grep IPAddress | grep --extended-regexp --only-matching "([0-9]{1,3}\.){3}[0-9]{1,3}")
echo "Using IP: $ip"
sed -i "s/TQ_S3_MEDIA_HOST: .*/TQ_S3_MEDIA_HOST: $ip/" overrides.yml
sed -i "s/TQ_S3_STATIC_HOST: .*/TQ_S3_STATIC_HOST: $ip/" overrides.yml
sed -i "s/TQ_S3_FINANCE_HOST: .*/TQ_S3_FINANCE_HOST: $ip/" overrides.yml
python scripts/generate_env.py # regenerate env to include the new overrides

echo "Finishing initialisation..."
mkdir -p logs

# Initialize minio
python scripts/initialize_minio.py

# Initialize django
python manage.py collectstatic --noinput -v 3
python manage.py migrate

# Load test data
python manage.py loaddata fixtures/*

echo "Done initialising TQ website."
