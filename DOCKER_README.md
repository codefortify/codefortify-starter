## CodefortifyAuth Docker Guide

This project supports two Docker Compose flows:

1. `docker-compose.yml`: local development (source mounted, `runserver`)
2. `docker-compose.prod.yml`: production-style runtime (`gunicorn`, no source bind mount)

Services:

- `web` (Django)
- `db` (PostgreSQL 16)
- `redis` (Redis 7)
- `celery` (Celery worker)
- `celery-beat` (optional profile)

Authentication note:

- Web and admin login accept either `email` or `username` with the same password.
- API token endpoints accept `identifier` (and still accept `email`/`username` for compatibility).
- If `username` is omitted during registration, it is auto-generated from email and normalized to lowercase underscores.

---

## 1) Prerequisites

- Docker Engine + Docker Compose v2
- Copy env template:

```bash
cp .env.example .env
```

Update at least:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`

---

## 2) Local Docker Development

Build images:

```bash
docker compose build
```

Start stack:

```bash
docker compose up -d
```

Stop stack:

```bash
docker compose down
```

Open app:

- `http://localhost:${APP_PORT:-8000}/`

Use `localhost` in the browser. Do not use `http://0.0.0.0:8000/` as the browser URL.

---

## 3) Common Commands

Run migrations:

```bash
docker compose exec web python manage.py migrate
```

Create superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Run tests:

```bash
docker compose exec web python manage.py test
```

Run shell:

```bash
docker compose exec web python manage.py shell
```

API login example:

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"identifier":"your_email_or_username","password":"your-password"}'
```

View logs:

```bash
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f db
docker compose logs -f redis
```

Celery beat (optional):

```bash
docker compose --profile beat up -d celery-beat
docker compose logs -f celery-beat
```

---

## 4) Production-Style Compose

Start with production compose:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Stop:

```bash
docker compose -f docker-compose.prod.yml down
```

Run migration manually:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

Notes:

- Set `CODEFORTIFY_ENVIRONMENT=production`
- Use strong `SECRET_KEY`
- Set real SMTP vars
- Keep `DEBUG=False`
- Do not expose DB/Redis ports publicly

---

## 5) PostgreSQL and Redis Notes

PostgreSQL data is persisted in `postgres_data` volume.

Redis uses `redis_data` volume with append-only enabled.

In Docker, `DATABASE_URL` is injected by Compose to use PostgreSQL. Outside Docker, leaving `DATABASE_URL` empty keeps SQLite fallback active.

---

## 6) Deployment Helper Script

Use:

```bash
./docker_deploy.sh up
```

Useful actions:

```bash
./docker_deploy.sh ps
./docker_deploy.sh logs web
./docker_deploy.sh migrate
./docker_deploy.sh test
./docker_deploy.sh down
```

Production compose with helper:

```bash
./docker_deploy.sh --prod up
```

---

## 7) Troubleshooting

`web` exits with DB errors:

- Confirm `db` is healthy: `docker compose ps`
- Check `.env` PostgreSQL credentials

Static file errors:

- Run: `docker compose exec web python manage.py collectstatic --noinput`

Celery cannot connect to Redis:

- Verify `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND`
- Check Redis logs: `docker compose logs redis`

Port already in use:

- Change `APP_PORT` in `.env`, then restart stack.
