#!/bin/bash
docker-compose run --rm django python3 manage.py loaddata fixtures/*
