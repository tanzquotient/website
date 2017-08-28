#!/usr/bin/env bash
docker-compose run -e LANG="en_US.UTF-8" -e LANGUAGE="en_US.UTF-8" -e LC_ALL="en_US.UTF-8" --rm django python3 scripts/generate_UML.py -o docs/dev/uml/ .
