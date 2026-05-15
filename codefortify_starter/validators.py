"""Validation and normalization helpers for CLI input."""

from __future__ import annotations

import keyword
import re
from dataclasses import dataclass

from codefortify_starter.constants import VALID_DATABASES


PROJECT_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
PROJECT_SLUG_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


class ValidationError(ValueError):
    """Raised when user-provided generator inputs are invalid."""


@dataclass(frozen=True)
class ProjectIdentity:
    """Normalized project naming attributes."""

    project_name: str
    project_slug: str
    project_title: str
    project_package: str
    project_class_name: str


def build_project_identity(raw_name: str) -> ProjectIdentity:
    """Validate and normalize the requested project name."""
    project_name = raw_name.strip()
    if not project_name:
        raise ValidationError("Project name cannot be empty.")
    if "/" in project_name or "\\" in project_name:
        raise ValidationError("Project name must not contain path separators.")
    if not PROJECT_NAME_RE.fullmatch(project_name):
        raise ValidationError(
            "Project name must start with a letter and contain only letters, numbers, hyphens, or underscores."
        )

    project_slug = project_name.lower().replace("-", "_")
    if not PROJECT_SLUG_RE.fullmatch(project_slug):
        raise ValidationError("Unable to build a valid Python package slug from the project name.")
    if keyword.iskeyword(project_slug):
        raise ValidationError(f"'{project_slug}' is a reserved Python keyword.")

    class_name = "".join(part.capitalize() for part in project_slug.split("_"))
    title = class_name or project_slug.capitalize()
    return ProjectIdentity(
        project_name=project_name,
        project_slug=project_slug,
        project_title=title,
        project_package=project_slug,
        project_class_name=class_name,
    )


def normalize_database(requested_database: str | None, *, use_docker: bool) -> str:
    """Resolve database selection defaults and validate explicit values."""
    if requested_database is None:
        return "postgres" if use_docker else "sqlite"

    database = requested_database.strip().lower()
    if database not in VALID_DATABASES:
        valid_values = ", ".join(VALID_DATABASES)
        raise ValidationError(f"Unsupported database '{requested_database}'. Choose one of: {valid_values}.")
    return database

