#!/bin/bash

# Pre-start script for the Tanzquotient website on the VSETH SIP
#
# Author: Thore Goebel <thgoebel@ethz.ch>
#
# Applies latest database migrations (which come from the code on Github)
# and collects static files. See official Django docs for more information.
#
# This script should be executed in the repository location (so that manage.py
# is correctly resolved).

# Apply the database migrations
python3 manage.py migrate

# Collect the static files and save them to STATIC_ROOT (defined in the Django
# project's settings.py)
python3 manage.py collectstatic --no-input

