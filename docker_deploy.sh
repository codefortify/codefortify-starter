#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"
ENV_FILE="${PROJECT_ROOT}/.env"
ENV_EXAMPLE="${PROJECT_ROOT}/.env.example"

COMPOSE_FILE="docker-compose.yml"
if [[ "${1:-}" == "--prod" ]]; then
  COMPOSE_FILE="docker-compose.prod.yml"
  shift
fi

ACTION="${1:-up}"
LOG_SERVICE="${2:-web}"

log() {
  printf '[docker_deploy] %s\n' "$*"
}

die() {
  printf '[docker_deploy][error] %s\n' "$*" >&2
  exit 1
}

usage() {
  cat <<EOF
Usage:
  ./docker_deploy.sh [--prod] [action] [service]

Actions:
  up            Build and start services, then run migrate/check
  down          Stop and remove services
  restart       Rebuild and restart services
  ps            Show container status
  logs [svc]    Tail logs (default service: web)
  migrate       Run Django migrations in web
  collectstatic Run collectstatic in web
  check         Run Django system checks in web
  test          Run Django tests in web
  shell         Open bash shell in web
EOF
}

ensure_docker() {
  command -v docker >/dev/null 2>&1 || die "Docker is not installed."
  docker info >/dev/null 2>&1 || die "Docker daemon is not reachable."
  docker compose version >/dev/null 2>&1 || die "Docker Compose v2 is required."
}

ensure_env_file() {
  if [[ ! -f "${ENV_FILE}" ]]; then
    [[ -f "${ENV_EXAMPLE}" ]] || die ".env is missing and .env.example was not found."
    cp "${ENV_EXAMPLE}" "${ENV_FILE}"
    log "Created .env from .env.example. Review values before production use."
  fi
}

compose() {
  docker compose --env-file "${ENV_FILE}" -f "${PROJECT_ROOT}/${COMPOSE_FILE}" "$@"
}

start_services() {
  log "Building images using ${COMPOSE_FILE}"
  compose build

  log "Starting database and redis"
  compose up -d db redis

  log "Starting web and celery"
  compose up -d web celery

  if [[ "${ENABLE_CELERY_BEAT:-false}" =~ ^(1|true|TRUE|yes|YES|on|ON)$ ]]; then
    log "Starting celery beat profile"
    compose --profile beat up -d celery-beat
  fi

  log "Running migrations"
  compose exec -T web python manage.py migrate --noinput

  if [[ "${COLLECT_STATIC_ON_DEPLOY:-false}" =~ ^(1|true|TRUE|yes|YES|on|ON)$ ]]; then
    log "Collecting static files"
    compose exec -T web python manage.py collectstatic --noinput
  fi

  log "Running Django system checks"
  compose exec -T web python manage.py check

  log "Service status"
  compose ps

  cat <<EOF

Useful commands:
  docker compose -f ${COMPOSE_FILE} logs -f web
  docker compose -f ${COMPOSE_FILE} logs -f celery
  docker compose -f ${COMPOSE_FILE} exec web python manage.py createsuperuser
  docker compose -f ${COMPOSE_FILE} exec web python manage.py test
EOF
}

ensure_docker
ensure_env_file

case "${ACTION}" in
  up)
    start_services
    ;;
  down)
    compose down
    ;;
  restart)
    compose down
    start_services
    ;;
  ps)
    compose ps
    ;;
  logs)
    compose logs -f "${LOG_SERVICE}"
    ;;
  migrate)
    compose exec -T web python manage.py migrate --noinput
    ;;
  collectstatic)
    compose exec -T web python manage.py collectstatic --noinput
    ;;
  check)
    compose exec -T web python manage.py check
    ;;
  test)
    compose exec -T web python manage.py test
    ;;
  shell)
    compose exec web bash
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage
    die "Unknown action: ${ACTION}"
    ;;
esac
