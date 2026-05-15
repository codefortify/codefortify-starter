#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[entrypoint] %s\n' "$*"
}

is_true() {
  case "${1:-}" in
    1|true|TRUE|True|yes|YES|on|ON) return 0 ;;
    *) return 1 ;;
  esac
}

resolve_db_from_database_url() {
  python - <<'PY'
import os
from urllib.parse import urlparse

database_url = (os.environ.get("DATABASE_URL") or "").strip()
if not database_url:
    print("|||")
    raise SystemExit

parsed = urlparse(database_url)
if parsed.scheme not in {"postgres", "postgresql", "pgsql"}:
    print("|||")
    raise SystemExit

host = parsed.hostname or ""
port = str(parsed.port or 5432)
user = parsed.username or os.environ.get("POSTGRES_USER", "postgres")
name = (parsed.path or "/").lstrip("/")
print(f"{host}|{port}|{user}|{name}")
PY
}

DB_HOST="${POSTGRES_HOST:-${DB_HOST:-}}"
DB_PORT="${POSTGRES_PORT:-${DB_PORT:-5432}}"
DB_USER="${POSTGRES_USER:-${DB_USER:-postgres}}"
DB_NAME="${POSTGRES_DB:-${DB_NAME:-postgres}}"

if [[ -z "${DB_HOST}" ]]; then
  IFS='|' read -r parsed_host parsed_port parsed_user parsed_name <<< "$(resolve_db_from_database_url)"
  if [[ -n "${parsed_host}" ]]; then
    DB_HOST="${parsed_host}"
    DB_PORT="${parsed_port:-5432}"
    DB_USER="${parsed_user:-postgres}"
    DB_NAME="${parsed_name:-postgres}"
  fi
fi

WAIT_TIMEOUT="${DB_WAIT_TIMEOUT:-120}"

mkdir -p /app/static_root /app/media_root /app/app_logs

if is_true "${WAIT_FOR_DB:-true}" && [[ -n "${DB_HOST}" ]]; then
  log "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT} (${DB_NAME})"
  start_ts="$(date +%s)"
  until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" >/dev/null 2>&1; do
    now_ts="$(date +%s)"
    if (( now_ts - start_ts > WAIT_TIMEOUT )); then
      log "PostgreSQL did not become ready within ${WAIT_TIMEOUT} seconds"
      exit 1
    fi
    sleep 1
  done
  log "PostgreSQL is ready"
fi

if is_true "${RUN_MIGRATIONS:-true}"; then
  log "Running database migrations"
  python manage.py migrate --noinput
fi

if is_true "${COLLECT_STATIC:-false}"; then
  log "Collecting static files"
  python manage.py collectstatic --noinput
fi

log "Starting: $*"
exec "$@"
