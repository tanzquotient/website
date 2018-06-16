sudo docker-compose run --rm django sh -c 'scripts/wait-for db:3306 -- python3 manage.py test --keepdb'
