# Dockerfile for the tanzquotient website
ARG AUTHORS="Thore Göbel <thgoebel@ethz.ch>, Daniel Sparber <daniel@sparber.io>"

# ===========================
# Base image
# ===========================
FROM python:3.14-slim AS base-image
ARG AUTHORS
LABEL org.opencontainers.image.authors="${AUTHORS}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    locales \
    openssl \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && sed --in-place '/en_US.UTF-8/s/^# //' /etc/locale.gen \
    && dpkg-reconfigure locales \
    && ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime \
    && dpkg-reconfigure tzdata

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US

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

# ===========================
# Builder Image
# ===========================
FROM base-image AS builder
ARG AUTHORS
LABEL org.opencontainers.image.authors="${AUTHORS}"

# Install build dependencies:
# - libpq-dev to build psycopg2 (which in turn is needed for the connection to postgres)
# - gettext to generate translations
# - pkg-config & libcairo2-dev are needed for building reportlab
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    build-essential \
    gettext \
    git \
    libcairo2-dev \
    libpq-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create python venv and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# ===========================
# App Image
# ===========================
FROM base-image AS app-image
ARG AUTHORS
LABEL org.opencontainers.image.authors="${AUTHORS}"

# Copy python venv from build
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Setup app directory
WORKDIR /app

# Copy the code into the container
COPY . .

# Ensure the scripts are executable
# Make sure log directory and files exist
RUN chmod +x scripts/generate_env_sip.sh \
    scripts/pre-start.sh \
    scripts/generate_env.py \
    scripts/post-start.sh \
    docker-entrypoint.sh && \
    mkdir -p logs && \
    touch logs/django.log \
          logs/tq.log \
          logs/payments.log \
          logs/errors.log

ENV AWS_DEFAULT_REGION=europe-west-2

# Change permissions on the code so the app-user can access it
RUN chown -R app-user:app-user /app

USER app-user

ENTRYPOINT ["/app/docker-entrypoint.sh"]