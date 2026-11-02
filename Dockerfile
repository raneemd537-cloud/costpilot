# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Security: run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Install Python dependencies (layer caches unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY web/ ./web/
COPY scripts/ ./scripts/

# Persistent data directory (override with DATABASE_URL for PostgreSQL)
RUN mkdir -p /data && chown appuser:appgroup /data
ENV DECISION_LAB_DATA=/data

# Production defaults — override per-deployment via environment variables
ENV DECISION_LAB_HOST=0.0.0.0
ENV DECISION_LAB_PORT=8765
ENV DECISION_LAB_TRUST_PROXY=1
ENV DECISION_LAB_SECURE_COOKIE=1

USER appuser

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/health')"

CMD ["python", "-m", "app.server"]
