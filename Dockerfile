# Dockerfile for the tanzquotient website
ARG AUTHORS="Thore Göbel <thgoebel@ethz.ch>, Daniel Sparber <daniel@sparber.io>"

# Base image
FROM eu.gcr.io/vseth-public/base:foxtrott AS base-image
# @Copyright    VSETH - Verband der Studierenden an der ETH Zürich
# Maybe we use our own base image at some point, vseth has no debian 13 image yet.

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

# Copy cinit file
COPY cinit.yml /etc/cinit.d/tq-website.yml

# Setup app directory
RUN mkdir -p /app
WORKDIR /app

# Copy the code into the container
COPY . .

# Ensure the scripts are executable
RUN pwd && ls && chmod +x scripts/generate_env_sip.sh && \
    chmod +x scripts/pre-start.sh && \
    chmod +x scripts/generate_env.py && \
    chmod +x scripts/post-start.sh

# Install requirements
RUN python3 -m pip install --upgrade pip --break-system-packages
RUN python3 -m pip install -r requirements.txt --break-system-packages

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

