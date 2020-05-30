#!/bin/bash

# Generate environment
./scripts/generate_env_override.py
./scripts/generate_env.py

# Build docker container
docker-compose build

# Initialize django
./scripts/collectstatic.sh
./scripts/migrate.sh
./scripts/loaddata.sh
