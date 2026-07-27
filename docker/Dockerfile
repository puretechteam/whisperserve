FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libsndfile1 curl libgomp1 ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh


FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libsndfile1 libgomp1 ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENV LOG_LEVEL=WARNING
ENV MODEL_NAME=base
ENV RELOAD=0

HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=40s \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]