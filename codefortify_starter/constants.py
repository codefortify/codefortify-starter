"""Shared constants for the starter generator."""

from __future__ import annotations

from typing import Final


PACKAGE_NAME: Final[str] = "codefortify-starter"
IMPORT_PACKAGE: Final[str] = "codefortify_starter"
CLI_COMMAND: Final[str] = "codefortify-startproject"
PACKAGE_VERSION: Final[str] = "1.0.0"

VALID_DATABASES: Final[tuple[str, ...]] = ("sqlite", "postgres", "mysql")

BASE_REQUIREMENTS: Final[tuple[str, ...]] = (
    "Django>=5.2,<5.3",
    "python-decouple>=3.8,<4.0",
)

FEATURE_REQUIREMENTS: Final[dict[str, tuple[str, ...]]] = {
    "htmx": ("django-htmx>=1.20.0,<2.0",),
    "drf": (
        "djangorestframework>=3.15.0,<4.0",
        "django-filter>=24.0,<26.0",
    ),
    "docker": (
        "gunicorn>=23.0.0,<24.0",
        "whitenoise>=6.8.0,<7.0",
    ),
    "celery": (
        "celery>=5.4.0,<6.0",
        "redis>=5.0.0,<6.0",
    ),
}

DATABASE_REQUIREMENTS: Final[dict[str, tuple[str, ...]]] = {
    "sqlite": (),
    "postgres": (
        "dj-database-url>=2.3.0,<3.0",
        "psycopg2-binary>=2.9.9,<3.0",
    ),
    "mysql": (
        "dj-database-url>=2.3.0,<3.0",
        "PyMySQL>=1.1.0,<2.0",
    ),
}

EXECUTABLE_FILES: Final[tuple[str, ...]] = ("entrypoint.sh", "docker_deploy.sh")
