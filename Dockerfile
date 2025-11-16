# Dockerfile for the tanzquotient website
ARG AUTHORS="Thore Göbel <thgoebel@ethz.ch>, Daniel Sparber <daniel@sparber.io>"

# Base image (copied and adaped from https://eu.gcr.io/vseth-public/base)
# @Copyright VSETH - Verband der Studierenden an der ETH Zürich
FROM debian:trixie-slim AS base-image
ARG AUTHORS
LABEL org.opencontainers.image.authors="${AUTHORS}"

ARG DEBIAN_FRONTEND='noninteractive'

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    locales \
    openssl \
    procps \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*  && \
    sed --in-place '/en_US.UTF-8/s/^# //' /etc/locale.gen && \
    dpkg-reconfigure locales

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US

RUN ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime && \
    dpkg-reconfigure tzdata

ENV IMAGE_APP_USERNAME=app-user
ENV IMAGE_APP_GROUPNAME=app-user
ENV IMAGE_APP_UID=1000
ENV IMAGE_APP_GID=1000

RUN groupadd "$IMAGE_APP_GROUPNAME" --gid "$IMAGE_APP_GID" && \
    useradd "$IMAGE_APP_USERNAME" \
        --uid "$IMAGE_APP_UID" \
        --gid "$IMAGE_APP_GID" \
        --home-dir /app \
        --create-home && \
    rm -rf /app/.bash* /app/.profile



# Builder Image
FROM base-image AS builder
ARG AUTHORS
LABEL org.opencontainers.image.authors="${AUTHORS}"

# Install build dependencies:
# - python
# - git to clone code from Github
# - libpq-dev to build psycopg2 (which in turn is needed for the connection to postgres)
# - gettext to generate translations
# - pkg-config & libcairo2-dev are needed for building reportlab
RUN apt update \
    && apt -y install --no-install-recommends \
    build-essential \
    gettext \
    libcairo2-dev \
    libpq-dev \
    pkg-config \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create python venv and install dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# App Image
FROM base-image AS app-image
ARG AUTHORS
LABEL org.opencontainers.image.authors="${AUTHORS}"

# Install runtime dependencies:
RUN apt update \
    && apt -y install --no-install-recommends \
    gettext \
    python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy python venv from build
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Setup app directory
RUN mkdir -p /app
WORKDIR /app

# Copy the code into the container
COPY . .

# Ensure the scripts are executable
RUN pwd && ls && chmod +x scripts/generate_env_sip.sh && \
    chmod +x scripts/pre-start.sh && \
    chmod +x scripts/generate_env.py && \
    chmod +x scripts/post-start.sh && \
    chmod +x docker-entrypoint.sh

# Make sure log directory and files exist
RUN mkdir -p logs && \
    touch logs/django.log && \
    touch logs/tq.log && \
    touch logs/payments.log && \
    touch logs/errors.log

RUN mkdir -p ~/.aws
RUN echo "[default]\nregion=europe-west-2" > ~/.aws/config

# Change permissions on the code so the app-user can access it
RUN chown -R app-user:app-user .

ENTRYPOINT ["/app/docker-entrypoint.sh"]