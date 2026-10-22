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
LABEL org.opencontainers.image.title="ifs-workorder-api" \
      org.opencontainers.image.description="IFS-style demo microservice for classroom" \
      org.opencontainers.image.vendor="IFS" \
      org.opencontainers.image.licenses="Proprietary"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_NAME=ifs-workorder-api \
    APP_ENV=dev \
    DB_HOST=db \
    DB_USER=ifs \
    DB_PASS=ifs \
    DB_NAME=ifsdb \
    RMQ_HOST=mq

# Non-root
RUN useradd -m -u 10001 appuser
WORKDIR /app

# Minimal runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 2) Install from wheels using the requirements file
COPY --from=builder /wheels /wheels
COPY app/requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# 3) Copy application (templates + static logo included)
COPY app/ /app/

USER appuser
EXPOSE 9000

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:9000/healthz || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host=0.0.0.0", "--port=9000"]
