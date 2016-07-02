#!/bin/sh
docker-compose -f docker-compose-production.yml run --rm django bash
