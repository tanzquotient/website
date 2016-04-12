FROM ubuntu:14.04
MAINTAINER martin.zellner@gmail.com

# Install Package Dependencies
RUN apt-get update && apt-get install -y --force-yes gettext python-virtualenv python-pip libmysqlclient-dev python-dev gcc gcc-multilib rabbitmq-server libjpeg-dev git libffi-dev python-cairo

RUN groupadd --system webapps && useradd  -ms /bin/bash --system --gid webapps --shell /bin/bash --home /webapps django

USER django
ADD requirements.txt /webapps/tq_website/requirements.txt
WORKDIR /webapps

USER  root
RUN pip install -r tq_website/requirements.txt

# Install supervisor (needed for production)
RUN apt-get update && apt-get install -y --force-yes supervisor


