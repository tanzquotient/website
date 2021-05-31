#!/bin/bash

# Pre-start script for the Tanzquotient website on the VSETH SIP
#
# Author: Thore Goebel <thgoebel@ethz.ch>
#
# Applies latest database migrations (which come from the code on Github).
# See official Django docs for more information.
# Loads dummy test data into database if TQ_DEBUG=True.
#
# This script should be executed in the repository location (so that manage.py
# is correctly resolved).
#
# All python manage.py commands will load the settings.py which in turns loads
# all environment variables needed from .env

# Apply the database migrations
python3 manage.py migrate

# Load dummy data
debug=`echo $TQ_DEBUG | awk '{print tolower($0)}'`
echo "$debug"
if [[ "$debug" == "true" ]]; then
    echo "Loading dummy data..."
    python3 manage.py loaddata fixtures/*
fi
