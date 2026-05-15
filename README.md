# codefortify-starter

`codefortify-starter` is a professional Django project starter generator for building clean, scalable, and production-ready Django applications faster.

It creates a modern Django architecture with a structured settings layout, reusable app organization, environment-based configuration, templates, static/media setup, and optional support for HTMX, Django REST Framework, Docker, Celery, Redis, PostgreSQL, and MySQL.

Whether you need a simple Django MVT project or a full API-ready Dockerized architecture with background workers, `codefortify-starter` gives you a consistent foundation for starting new projects.

## What It Is

`codefortify-starter` is a PyPI-installable Django project generator that helps developers quickly scaffold clean, maintainable, production-ready Django architectures.

By default, it generates a simple Django MVT project. With flags, it can add HTMX, DRF, Docker, Celery, Redis, PostgreSQL, and MySQL.

## Why It Exists

Most Django projects repeat the same setup work: project layout, settings split, dependency wiring, env bootstrapping, and deployment scaffolding. `codefortify-starter` reduces that repeated effort and standardizes project initialization.

## Who Should Use It

- Django developers starting new applications
- Teams that want a consistent starter architecture
- Backend/API engineers who need optional DRF, Docker, and Celery setup
- Developers who want a lightweight alternative to larger templating frameworks

## Installation

Install from PyPI:

```bash
pip install codefortify-starter
```

Install an exact version:

```bash
pip install codefortify-starter==1.0.0
```

Verify the CLI:

```bash
codefortify-startproject --help
```

## Quick Start

Create a basic Django MVT project:

```bash
codefortify-startproject myproject
cd myproject
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Supported CLI Flags

- `--htmx`
- `--drf`
- `--docker`
- `--celery`
- `--database [sqlite|postgres|mysql]`
- `--no-git`
- `--force`
- `--directory PATH`
- `--all`

## Command Examples

```bash
codefortify-startproject myproject
codefortify-startproject myproject --htmx
codefortify-startproject myproject --drf
codefortify-startproject myproject --docker
codefortify-startproject myproject --celery
codefortify-startproject myproject --docker --celery
codefortify-startproject myproject --drf --docker --celery
codefortify-startproject myproject --database postgres
codefortify-startproject myproject --database mysql
codefortify-startproject myproject --no-git
codefortify-startproject myproject --force
codefortify-startproject myproject --directory /path/to/projects
codefortify-startproject myproject --all
```

`--all` is equivalent to:

```bash
codefortify-startproject myproject --htmx --drf --docker --celery --database postgres
```

## Feature Matrix

| Feature | Flag | Description |
|---|---|---|
| Django MVT | default | Clean Django project with settings, templates, static/media, and home app |
| HTMX | `--htmx` | Adds `django-htmx`, middleware, and example partial views |
| Django REST Framework | `--drf` | Adds DRF, API app, API routes, serializers, and tests |
| Docker | `--docker` | Adds Dockerfile, docker-compose, entrypoint, deployment script, and Docker docs |
| Celery + Redis | `--celery` | Adds Celery config, Redis broker settings, and example task |
| PostgreSQL | `--database postgres` | Adds PostgreSQL-ready configuration |
| MySQL | `--database mysql` | Adds MySQL-ready configuration |
| Full stack | `--all` | Adds HTMX, DRF, Docker, Celery, Redis, and PostgreSQL |

## Generated Architecture

```text
myproject/
├── apps/
│   └── home/
├── core/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

Feature-specific files are added only when their flags are selected (for example `apps/api`, `core/celery.py`, `Dockerfile`, compose files, and task modules).

## Database Options

- Default without `--docker`: SQLite
- Default with `--docker`: PostgreSQL
- Explicit: `--database postgres`, `--database mysql`, or `--database sqlite`

Generated settings safely handle an empty `DATABASE_URL` and support local fallback behavior for development.

## HTMX Usage

Generate with HTMX:

```bash
codefortify-startproject myproject --htmx
```

The generated project includes HTMX middleware and an example partial endpoint.

## DRF Usage

Generate with DRF:

```bash
codefortify-startproject myproject --drf
```

The generated API app includes a health endpoint:

- `GET /api/health/`

## Docker Usage

```bash
codefortify-startproject myproject --docker
cd myproject
cp .env.example .env
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
```

## Celery Usage

Generate with Celery support:

```bash
codefortify-startproject myproject --celery
```

Run worker locally:

```bash
celery -A core worker -l info
```

## Full Stack Usage

```bash
codefortify-startproject myproject --all
cd myproject
cp .env.example .env
docker compose build
docker compose up -d
docker compose ps
```

## Local Development (This Package)

```bash
python -m venv .pkgvenv
source .pkgvenv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m pytest -q tests
```

## Build and Publish

Build and validate:

```bash
rm -rf dist build *.egg-info
python -m build
twine check dist/*
```

Publish to TestPyPI:

```bash
twine upload --repository testpypi dist/*
```

Publish to PyPI:

```bash
twine upload dist/*
```

## Testing from TestPyPI

Use this only for testing pre-release package builds:

```bash
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  codefortify-starter==1.0.0
```

## License

MIT License. See [LICENSE](LICENSE).
