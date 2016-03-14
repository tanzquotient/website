FROM ubuntu:14.04
MAINTAINER martin.zellner@gmail.com

# Install Package Dependencies
RUN apt-get update && apt-get install -y --force-yes python-virtualenv python-pip mysql-server libmysqlclient-dev python-dev gcc gcc-multilib rabbitmq-server libjpeg-dev git

RUN pip install -I pillow

ADD . ~/code
WORKDIR ~/code

RUN pip install -r requirements.txt