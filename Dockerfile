# Multi-stage Dockerfile for WatsonX Agent Creator
# Optimized for production deployment with minimal image size

# ============================================================================
# Stage 1: Builder - Install dependencies and build application
# ============================================================================
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install UV for lightning-fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create application directory
WORKDIR /build

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Copy source code
COPY src/ ./src/
COPY assets/ ./assets/

# Install dependencies and build wheel
RUN uv pip install --system --compile-bytecode .

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.12-slim

# Security: Create non-root user
RUN groupadd -r watsonx && \
    useradd -r -g watsonx -s /bin/bash -d /app watsonx

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH" \
    PYTHONPATH="/app"

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/watsonx-agent /usr/local/bin/watsonx-agent
COPY --from=builder /usr/local/bin/wxa /usr/local/bin/wxa

# Copy application files
COPY --from=builder /build/src ./src
COPY --from=builder /build/assets ./assets

# Change ownership to non-root user
RUN chown -R watsonx:watsonx /app

# Switch to non-root user
USER watsonx

# Create output directory for generated agents
RUN mkdir -p /app/agents

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import watsonx_agent_creator; print('OK')" || exit 1

# Set entrypoint
ENTRYPOINT ["watsonx-agent"]

# Default command
CMD ["--help"]

# Labels for metadata
LABEL maintainer="Ruslan Magana <contact@ruslanmv.com>" \
      version="2.0.0" \
      description="Lightning-fast AI agent scaffolding for IBM watsonx.ai" \
      org.opencontainers.image.source="https://github.com/ruslanmv/watsonx-agent-creator" \
      org.opencontainers.image.licenses="Apache-2.0"
