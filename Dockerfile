# Dockerfile for the tanzquotient website
ARG AUTHORS="Thore Göbel <thgoebel@ethz.ch>, Daniel Sparber <daniel@sparber.io>"

# ===========================
# Base image
# ===========================
FROM python:3.15-slim AS base-image
ARG AUTHORS
LABEL org.opencontainers.image.authors="${AUTHORS}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Europe/Zurich

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

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.12.23@sha256:61d393e44e249f2e4b526b6c7ddcecce245946826e608e11c93ad4f5bba55b21 /uv /uvx /bin/

ENV UV_NO_DEV=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_LINK_MODE=copy

COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

COPY . .

# Install project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable

# ===========================
# App Image
# ===========================
FROM base-image AS app-image
ARG AUTHORS
LABEL org.opencontainers.image.authors="${AUTHORS}"

# Copy python venv from build
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

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