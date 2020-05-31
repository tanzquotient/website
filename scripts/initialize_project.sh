#!/bin/bash

# Generate environment
./scripts/generate_env_override.py
./scripts/generate_env.py

# Build docker container
docker-compose build

# Initialize minio
./scripts/initialize_minio.sh

# Initialize django
./scripts/collectstatic.sh
./scripts/migrate.sh

# Load test data
./scripts/loaddata.sh
