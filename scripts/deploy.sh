#!/usr/bin/env bash
usage="deployment script

$(basename "$0") [-h] [-f file]

where:
    -h  show this help text
    -f  specify the docker-compose file (default is defined in .env)"

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
docker_file="docker-compose.yml"
load=0

while getopts "h?lf:" opt; do
    case "$opt" in
    h|\?)
        echo "$usage"
        exit 0
        ;;
    f)  docker_file=$OPTARG
        ;;
    esac
done

docker-compose -f $docker_file run --rm django python3 manage.py migrate
# docker-compose -f $docker_file run --rm django python3 manage.py loaddata fixtures/*
docker-compose -f $docker_file run --rm django python3 manage.py collectstatic --no-input

echo 'DEPLOYED'

# End of file