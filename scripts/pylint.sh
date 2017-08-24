#!/usr/bin/env bash
if [ -z "$1" ]
  then
    echo "Usage:"
    echo "pylint.sh [dir or modulename]"
    echo ""
    echo "Example:"
    echo "pylint.sh events"
else
    docker-compose run --rm django python3 -m pylint -j 0 $1
fi
