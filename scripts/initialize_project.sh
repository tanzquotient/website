#!/bin/bash

# Generate environment
./scripts/generate_env_override.py
./scripts/generate_env.py

# Build docker container
echo "Building container images..."
docker-compose build

# Workaround for local minio development
#
# The problem is that "localhost" is not a valid value from the perspective
# of the Django container accessing Minio, and "tq-data" is not a valid value
# from the perspective of your browser accessing Minio.
echo "Setting IPs for Minio..."
ip=$(docker inspect tq-data | grep IPAddress | grep --extended-regexp --only-matching "([0-9]{1,3}\.){3}[0-9]{1,3}")
sed -i "s/TQ_S3_MEDIA_HOST: overrideme/TQ_S3_MEDIA_HOST: $ip/" overrides.yml
sed -i "s/TQ_S3_STATIC_HOST: overrideme/TQ_S3_STATIC_HOST: $ip/" overrides.yml
sed -i "s/TQ_S3_POSTFINANCE_HOST: overrideme/TQ_S3_POSTFINANCE_HOST: $ip/" overrides.yml
./scripts/generate_env.py # regenerate env to include the new overrides

echo "Finishing initialisation..."

# Initialize minio
./scripts/initialize_minio.sh

# Initialize django
./scripts/collectstatic.sh
./scripts/migrate.sh

# Load test data
./scripts/loaddata.sh
