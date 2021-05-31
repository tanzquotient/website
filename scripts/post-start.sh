#!/bin/bash

# Post-start script for the Tanzquotient website on the VSETH SIP
#
# Author: Daniel Sparber <dsparber@ethz.ch>
#
# Collect the static files and save them to STATIC_ROOT (defined in the Django
# project's settings.py)

python3 manage.py collectstatic --no-input -v 3

