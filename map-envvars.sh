#!/bin/bash

# Script to map SIP-specific env vars TQ-specific env vars
#
# Author: Thore Goebel <thgoebel@ethz.ch>
#
# Copies the .env-template to .env
# and writes all the SIP_ environment variables into it.
#
# This can be very fragile and is liable to break, e.g. if:
#  - the .env-template format changes
#  - SIP environment variables change, e.g. due to renaming an S3 bucket in sip.yml
#
# Usage:
# map-envvars.sh <from> <to>
#       <from>  source path of .env-template
#       <to>    destination path for .env

# Check if we got two arguments
if [[  $# -ne 2 ]]
then
    echo ""
    exit 1
fi

TEMPLATE="$1"
ENV="$2"

# Copy .env into the right location
cp "$TEMPLATE" "$ENV"

# Template to copy sed replace command from :-)
#sed -i "s///g" "$ENV"

# Django debug
sed -i "s/^TQ_DEBUG=.*/TQ_DEBUG=False/g" "$ENV"

# Secret
# TODO
sed -i "s/^TQ_SECRET_KEY=.*/TQ_SECRET_KEY=$XXX/g" "$ENV"

# Postgres
sed -i "s/^TQ_DB_HOST_POSTGRES=.*/TQ_DB_HOST_POSTGRES=$SIP_/g" "$ENV"
sed -i "s/^TQ_DB_PORT_POSTGRES=.*/TQ_DB_PORT_POSTGRES=$SIP_/g" "$ENV"
sed -i "s/^TQ_DB_USER_POSTGRES=.*/TQ_DB_USER_POSTGRES=$SIP_/g" "$ENV"
sed -i "s/^TQ_DB_PASSWORD_POSTGRES=.*/TQ_DB_PASSWORD_POSTGRES=$SIP_/g" "$ENV"

# S3 - media
sed -i "s/^TQ_S3_ENABLED=.*/TQ_S3_ENABLED=True/g" "$ENV"
sed -i "s/^=.*/=$SIP_S3_TQ_MEDIA_HOST/g" "$ENV"
sed -i "s/^=.*/=$SIP_S3_TQ_MEDIA_PORT/g" "$ENV"
sed -i "s/^=.*/=$SIP_S3_TQ_MEDIA_BUCKET/g" "$ENV"
sed -i "s/^=.*/=$SIP_S3_TQ_MEDIA_ACCESS_KEY/g" "$ENV"
sed -i "s/^=.*/=$SIP_S3_TQ_MEDIA_SECRET_KEY/g" "$ENV"
sed -i "s/^=.*/=$SIP_S3_TQ_MEDIA_USE_SSL/g" "$ENV"

# TODO
# S3 - static
# S3 - postfinance

# Redis
# TODO which env var is this on SIP?
sed -i "s/^REDIS_BROKER_URL=.*/REDIS_BROKER_URL=$SIP_REDIS/g" "$ENV"

# Email
# TODO
sed -i "s/^TQ_EMAIL_HOST=.*/TQ_EMAIL_HOST=$XXX/g" "$ENV"
sed -i "s/^TQ_EMAIL_PORT=.*/TQ_EMAIL_PORT=$XXX/g" "$ENV"
sed -i "s/^TQ_EMAIL_USE_TLS=.*/TQ_EMAIL_USE_TLS=True/g" "$ENV"
sed -i "s/^TQ_EMAIL_HOST_USER=.*/TQ_EMAIL_HOST_USER=$XXX/g" "$ENV"
sed -i "s/^TQ_EMAIL_HOST_PASSWORD=.*/TQ_EMAIL_HOST_PASSWORD=$XXX/g" "$ENV"
sed -i "s/^TQ_DEFAULT_FROM_EMAIL=.*/TQ_DEFAULT_FROM_EMAIL=$XXX/g" "$ENV"

# Google Analytics
# TODO how to
sed -i "s/^TQ_GOOGLE_ANALYTICS_PROPERTY_ID=.*/TQ_GOOGLE_ANALYTICS_PROPERTY_ID=$NONEXISTING/g" "$ENV"

# FDS - postfinance
# TODO
# TODO ssh key (???)
sed -i "s/^TQ_FDS_USER=.*/TQ_FDS_USER=$XXX/g" "$ENV"

# Postfinance account
# TODO
sed -i "s/^TQ_PAYMENT_ACCOUNT_IBAN=.*/TQ_PAYMENT_ACCOUNT_IBAN=$XXX/g" "$ENV"
sed -i "s/^TQ_PAYMENT_ACCOUNT_SWIFT=.*/TQ_PAYMENT_ACCOUNT_SWIFT=$XXX/g" "$ENV"
sed -i "s/^TQ_PAYMENT_ACCOUNT_POST_NUMBER=.*/TQ_PAYMENT_ACCOUNT_POST_NUMBER=$XXX/g" "$ENV"
sed -i "s/^TQ_PAYMENT_ACCOUNT_RECIPIENT=.*/TQ_PAYMENT_ACCOUNT_RECIPIENT=$XXX/g" "$ENV"
sed -i "s/^TQ_PAYMENT_ACCOUNT_RECIPIENT_ZIPCODE_CITY=.*/TQ_PAYMENT_ACCOUNT_RECIPIENT_ZIPCODE_CITY=$XXX/g" "$ENV"

