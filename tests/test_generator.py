from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codefortify_starter.generator import StarterProjectGenerator, build_generation_options
from codefortify_starter.validators import build_project_identity, normalize_database


def _requirements_packages(project_path: Path) -> set[str]:
    packages: set[str] = set()
    for line in (project_path / "requirements.txt").read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        for separator in ("==", ">=", "<=", "~=", ">", "<"):
            if separator in raw:
                raw = raw.split(separator, 1)[0].strip()
                break
        packages.add(raw.lower())
    return packages


def _assert_no_unresolved_tokens(testcase: unittest.TestCase, project_path: Path) -> None:
    for path in sorted(project_path.rglob("*")):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        testcase.assertNotIn("[[", content, msg=f"Unresolved token in {path}")
        testcase.assertNotIn("[%", content, msg=f"Unresolved block token in {path}")


class GeneratorTests(unittest.TestCase):
    def _generate(
        self,
        root: Path,
        name: str,
        *,
        htmx: bool = False,
        drf: bool = False,
        docker: bool = False,
        celery: bool = False,
        database: str | None = None,
        no_git: bool = True,
        force: bool = False,
    ) -> Path:
        identity = build_project_identity(name)
        resolved_database = normalize_database(database, use_docker=docker)
        options = build_generation_options(
            project_name=identity.project_name,
            project_slug=identity.project_slug,
            project_title=identity.project_title,
            project_package=identity.project_package,
            project_class_name=identity.project_class_name,
            directory=root,
            database=resolved_database,
            use_htmx=htmx,
            use_drf=drf,
            use_docker=docker,
            use_celery=celery,
            no_git=no_git,
            force=force,
        )
        generator = StarterProjectGenerator()
        result = generator.generate(options)
        return result.project_path

    def test_generation_matrix_and_requirements(self):
        cases = [
            {
                "name": "basic",
                "flags": {},
                "must_have": {"django", "python-decouple"},
                "must_not_have": {
                    "django-htmx",
                    "djangorestframework",
                    "celery",
                    "gunicorn",
                    "dj-database-url",
                },
                "must_have_paths": ["manage.py", "core/settings/base.py", "apps/home/views.py"],
                "must_not_have_paths": ["Dockerfile", "apps/api", "core/celery.py"],
            },
            {
                "name": "htmx",
                "flags": {"htmx": True},
                "must_have": {"django-htmx"},
                "must_not_have": {"djangorestframework", "celery", "gunicorn"},
                "must_have_paths": ["templates/partials/example.html"],
                "must_not_have_paths": ["apps/api", "Dockerfile", "core/celery.py"],
            },
            {
                "name": "drf",
                "flags": {"drf": True},
                "must_have": {"djangorestframework", "django-filter"},
                "must_not_have": {"celery", "gunicorn"},
                "must_have_paths": ["apps/api/views.py", "apps/api/serializers.py"],
                "must_not_have_paths": ["Dockerfile", "core/celery.py"],
            },
            {
                "name": "docker",
                "flags": {"docker": True},
                "must_have": {"gunicorn", "whitenoise", "dj-database-url", "psycopg2-binary"},
                "must_not_have": {"djangorestframework", "celery"},
                "must_have_paths": ["Dockerfile", "docker-compose.yml", "docker-compose.prod.yml", "entrypoint.sh"],
                "must_not_have_paths": ["apps/api", "core/celery.py"],
            },
            {
                "name": "celery",
                "flags": {"celery": True},
                "must_have": {"celery", "redis"},
                "must_not_have": {"djangorestframework", "gunicorn"},
                "must_have_paths": ["core/celery.py", "apps/home/tasks.py"],
                "must_not_have_paths": ["Dockerfile", "apps/api"],
            },
            {
                "name": "docker_celery",
                "flags": {"docker": True, "celery": True},
                "must_have": {"celery", "redis", "gunicorn", "whitenoise", "psycopg2-binary"},
                "must_not_have": {"djangorestframework"},
                "must_have_paths": ["Dockerfile", "core/celery.py", "docker-compose.yml"],
                "must_not_have_paths": ["apps/api"],
            },
            {
                "name": "drf_docker_celery",
                "flags": {"drf": True, "docker": True, "celery": True},
                "must_have": {
                    "djangorestframework",
                    "django-filter",
                    "celery",
                    "redis",
                    "gunicorn",
                    "whitenoise",
                    "psycopg2-binary",
                },
                "must_not_have": {"django-htmx"},
                "must_have_paths": ["apps/api/views.py", "core/celery.py", "Dockerfile"],
                "must_not_have_paths": [],
            },
            {
                "name": "all",
                "flags": {"htmx": True, "drf": True, "docker": True, "celery": True},
                "must_have": {
                    "django-htmx",
                    "djangorestframework",
                    "django-filter",
                    "celery",
                    "redis",
                    "gunicorn",
                    "whitenoise",
                    "psycopg2-binary",
                },
                "must_not_have": {"pymysql"},
                "must_have_paths": ["templates/partials/example.html", "apps/api/views.py", "core/celery.py", "Dockerfile"],
                "must_not_have_paths": [],
            },
            {
                "name": "postgres_db",
                "flags": {"database": "postgres"},
                "must_have": {"dj-database-url", "psycopg2-binary"},
                "must_not_have": {"pymysql"},
                "must_have_paths": ["core/settings/base.py"],
                "must_not_have_paths": [],
            },
            {
                "name": "mysql_db",
                "flags": {"database": "mysql"},
                "must_have": {"dj-database-url", "pymysql"},
                "must_not_have": {"psycopg2-binary"},
                "must_have_paths": ["core/settings/base.py"],
                "must_not_have_paths": [],
            },
        ]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for case in cases:
                with self.subTest(case=case["name"]):
                    project = self._generate(root, case["name"], **case["flags"])
                    self.assertTrue(project.exists())
                    _assert_no_unresolved_tokens(self, project)

                    packages = _requirements_packages(project)
                    self.assertEqual(
                        len(packages),
                        len((project / "requirements.txt").read_text(encoding="utf-8").splitlines()),
                        msg=f"Duplicate requirements found in {project / 'requirements.txt'}",
                    )

                    for package in case["must_have"]:
                        self.assertIn(package, packages, msg=f"{package} missing for {case['name']}")
                    for package in case["must_not_have"]:
                        self.assertNotIn(package, packages, msg=f"{package} unexpectedly present for {case['name']}")

                    for relative_path in case["must_have_paths"]:
                        self.assertTrue((project / relative_path).exists(), msg=f"Missing {relative_path}")
                    for relative_path in case["must_not_have_paths"]:
                        self.assertFalse((project / relative_path).exists(), msg=f"Unexpected {relative_path}")

    def test_directory_and_no_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "output-root"
            project = self._generate(nested, "directory_target", no_git=True)
            self.assertTrue(project.exists())
            self.assertFalse((project / ".git").exists())

    def test_existing_folder_fails_without_force_and_works_with_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "existing_force"
            existing.mkdir()

            with self.assertRaises(FileExistsError):
                self._generate(root, "existing_force", force=False)

            project = self._generate(root, "existing_force", force=True)
            self.assertTrue((project / "manage.py").exists())

    def test_docker_postgres_templates_use_safe_database_url_handling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self._generate(root, "docker_safe", docker=True)

            settings_content = (project / "core/settings/base.py").read_text(encoding="utf-8")
            self.assertIn('DATABASE_URL = config("DATABASE_URL", default="").strip()', settings_content)
            self.assertIn("if DATABASE_URL:", settings_content)
            self.assertIn('"ENGINE": "django.db.backends.sqlite3"', settings_content)
            self.assertNotIn("DEFAULT_DATABASE_URL", settings_content)
            self.assertNotIn('dj_database_url.parse("")', settings_content)

            env_example = (project / ".env.example").read_text(encoding="utf-8")
            self.assertIn("# DATABASE_URL=sqlite:///db.sqlite3", env_example)
            self.assertIn("# DATABASE_URL=postgres://docker_safe:docker_safe@db:5432/docker_safe", env_example)
            self.assertIn("DATABASE_URL=", env_example)

            compose_content = (project / "docker-compose.yml").read_text(encoding="utf-8")
            self.assertIn(
                "DATABASE_URL: postgres://${POSTGRES_USER:-docker_safe}:${POSTGRES_PASSWORD:-change-me}@db:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-docker_safe}",
                compose_content,
            )

    def test_postgres_database_template_uses_safe_database_url_handling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self._generate(root, "postgres_safe", database="postgres")

            settings_content = (project / "core/settings/base.py").read_text(encoding="utf-8")
            self.assertIn('DATABASE_URL = config("DATABASE_URL", default="").strip()', settings_content)
            self.assertIn("if DATABASE_URL:", settings_content)
            self.assertIn('"ENGINE": "django.db.backends.sqlite3"', settings_content)
            self.assertNotIn("DEFAULT_DATABASE_URL", settings_content)
