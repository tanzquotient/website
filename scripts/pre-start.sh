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

# Migrate to Django CMS 4 (can be removed once Django CMS 4 is up and running)
python manage.py cms4_migration

# Apply the database migrations
python3 manage.py migrate

# Whenever we register a model with django-reversion this command needs to be run
python3 manage.py createinitialrevisions

# Django CMS stuff
python3 -Wa manage.py cms check
python3 manage.py cms fix-tree

# Load dummy data
debug=`echo $TQ_DEBUG | awk '{print tolower($0)}'`
echo "$debug"
if [[ "$debug" == "true" ]]; then
    echo "Loading dummy data..."
    python3 manage.py loaddata fixtures/*
fi
