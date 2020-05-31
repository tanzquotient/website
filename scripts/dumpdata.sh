#!/bin/bash
docker-compose run --rm django python manage.py dumpdata "$1" --format json --indent 2 > "fixtures/$1.json"