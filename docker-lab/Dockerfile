# --- Builder stage
FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
# 1) Copy requirements and wheel the FULL dependency graph (NO --no-deps)
COPY app/requirements.txt .
# trusted-host: classroom build on a network that intercepts HTTPS
RUN python -m pip install --upgrade pip wheel setuptools \
      --trusted-host pypi.org --trusted-host files.pythonhosted.org \
 && pip wheel --no-cache-dir \
      --trusted-host pypi.org --trusted-host files.pythonhosted.org \
      -r requirements.txt -w /wheels

# --- Runtime stage
FROM python:3.12-slim AS runtime
LABEL org.opencontainers.image.title="sams-burger-stall" \
      org.opencontainers.image.description="Sam's burger stall: a classroom app for learning Docker" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_NAME=cashier \
    APP_ENV=dev \
    DB_HOST=cabinet \
    DB_USER=sam \
    DB_PASS=sam \
    DB_NAME=stall \
    RMQ_HOST=bell

# Non-root. The notebook folder belongs to the app user, so a new volume mounted there is writable.
RUN useradd -m -u 10001 appuser \
 && mkdir /notebook && chown appuser /notebook
WORKDIR /app

# Minimal runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 2) Install from wheels using the requirements file
COPY --from=builder /wheels /wheels
COPY app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# 3) Copy application (templates and static files included)
COPY app/ /app/

USER appuser
EXPOSE 9000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:9000/healthz || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host=0.0.0.0", "--port=9000"]
