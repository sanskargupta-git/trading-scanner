FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# One worker keeps the background refresh thread and its cache single-copy;
# threads handle concurrent page loads. Requests are served from cache, so the
# timeout only needs to cover slow clients, not Yahoo Finance.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 8 --timeout 120 --access-logfile - trading_scanner:app"]
