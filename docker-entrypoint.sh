#!/bin/bash

set -euo pipefail

# Map Elastic Beanstalk RDS metadata to the PG* values Django expects
export PGHOST="${PGHOST:-${RDS_HOSTNAME:-localhost}}"
export PGPORT="${PGPORT:-${RDS_PORT:-5432}}"
export PGDATABASE="${PGDATABASE:-${RDS_DB_NAME:-postgres}}"
export PGUSER="${PGUSER:-${RDS_USERNAME:-postgres}}"
export PGPASSWORD="${PGPASSWORD:-${RDS_PASSWORD:-}}"

if [[ -z "${PGHOST}" || -z "${PGDATABASE}" || -z "${PGUSER}" ]]; then
  echo "[entrypoint] Missing database configuration (PGHOST/PGDATABASE/PGUSER)" >&2
  exit 1
fi

echo "[entrypoint] Database configuration"
echo "  Host: ${PGHOST}"
echo "  Port: ${PGPORT}"
echo "  Database: ${PGDATABASE}"
echo "  User: ${PGUSER}"

if [[ -z "${PGPASSWORD}" ]]; then
  echo "[entrypoint] Warning: PGPASSWORD is empty; authentication may fail" >&2
fi

python <<'PY'
import os
import time
import psycopg

host = os.environ["PGHOST"]
port = int(os.environ.get("PGPORT", "5432"))
dbname = os.environ["PGDATABASE"]
user = os.environ["PGUSER"]
password = os.environ.get("PGPASSWORD")
attempts = int(os.environ.get("DB_MAX_ATTEMPTS", "60"))
delay = float(os.environ.get("DB_RETRY_DELAY", "2"))

for attempt in range(1, attempts + 1):
    try:
        with psycopg.connect(host=host, port=port, dbname=dbname, user=user, password=password, connect_timeout=5):
            break
    except Exception as exc:  # pragma: no cover
        if attempt == attempts:
            raise
        print(f"[entrypoint] Database not ready ({exc}); retrying {attempt}/{attempts} in {delay}s", flush=True)
        time.sleep(delay)
PY

echo "[entrypoint] Applying migrations"
python manage.py migrate --noinput

echo "[entrypoint] Collecting static files"
python manage.py collectstatic --noinput

echo "[entrypoint] Starting Gunicorn"
exec gunicorn \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers ${GUNICORN_WORKERS:-3} \
  --timeout ${GUNICORN_TIMEOUT:-120} \
  frequenza_libera.wsgi:application
