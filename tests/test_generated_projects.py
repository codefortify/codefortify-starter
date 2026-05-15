from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from codefortify_starter.generator import StarterProjectGenerator, build_generation_options
from codefortify_starter.validators import build_project_identity, normalize_database


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


class GeneratedProjectRuntimeTests(unittest.TestCase):
    def _generate(
        self,
        root: Path,
        name: str,
        *,
        drf: bool = False,
        docker: bool = False,
        celery: bool = False,
        htmx: bool = False,
        database: str | None = None,
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
            no_git=True,
            force=False,
        )
        generator = StarterProjectGenerator()
        result = generator.generate(options)
        return result.project_path

    def _run_manage(self, project: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "manage.py", *args],
            cwd=project,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    @unittest.skipUnless(_module_available("django"), "Django is not installed in test environment")
    def test_basic_project_check_migrate_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self._generate(Path(tmp), "runtime_basic")
            env = os.environ.copy()
            env.setdefault("CODEFORTIFY_ENVIRONMENT", "dev")

            check = subprocess.run(
                [sys.executable, "manage.py", "check"],
                cwd=project,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(check.returncode, 0, msg=check.stderr)

            migrate = subprocess.run(
                [sys.executable, "manage.py", "migrate", "--noinput"],
                cwd=project,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(migrate.returncode, 0, msg=migrate.stderr)

            tests = subprocess.run(
                [sys.executable, "manage.py", "test"],
                cwd=project,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(tests.returncode, 0, msg=tests.stderr)

    @unittest.skipUnless(
        _module_available("django") and _module_available("rest_framework"),
        "Django/DRF are not installed in test environment",
    )
    def test_drf_project_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self._generate(Path(tmp), "runtime_drf", drf=True)
            env = os.environ.copy()
            env.setdefault("CODEFORTIFY_ENVIRONMENT", "dev")

            check = subprocess.run(
                [sys.executable, "manage.py", "check"],
                cwd=project,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(check.returncode, 0, msg=check.stderr)

    @unittest.skipUnless(
        _module_available("django")
        and _module_available("dj_database_url")
        and _module_available("whitenoise"),
        "Django/dj-database-url/whitenoise are not installed in test environment",
    )
    def test_docker_project_local_env_example_check_migrate_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self._generate(Path(tmp), "runtime_docker_local", docker=True)
            (project / ".env").write_text((project / ".env.example").read_text(encoding="utf-8"), encoding="utf-8")
            env = os.environ.copy()
            env.setdefault("CODEFORTIFY_ENVIRONMENT", "dev")

            check = self._run_manage(project, env, "check")
            self.assertEqual(check.returncode, 0, msg=check.stderr)

            migrate = self._run_manage(project, env, "migrate", "--noinput")
            self.assertEqual(migrate.returncode, 0, msg=migrate.stderr)

            tests = self._run_manage(project, env, "test")
            self.assertEqual(tests.returncode, 0, msg=tests.stderr)

    @unittest.skipUnless(
        _module_available("django") and _module_available("dj_database_url"),
        "Django/dj-database-url are not installed in test environment",
    )
    def test_postgres_project_blank_database_url_still_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self._generate(Path(tmp), "runtime_postgres_local", database="postgres")
            (project / ".env").write_text((project / ".env.example").read_text(encoding="utf-8"), encoding="utf-8")
            env = os.environ.copy()
            env.setdefault("CODEFORTIFY_ENVIRONMENT", "dev")

            check = self._run_manage(project, env, "check")
            self.assertEqual(check.returncode, 0, msg=check.stderr)

    @unittest.skipUnless(shutil.which("docker"), "Docker CLI is not installed")
    def test_docker_compose_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = self._generate(Path(tmp), "runtime_docker", docker=True, celery=True)
            (project / ".env").write_text((project / ".env.example").read_text(encoding="utf-8"), encoding="utf-8")
            config = subprocess.run(
                ["docker", "compose", "-f", "docker-compose.yml", "config"],
                cwd=project,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(config.returncode, 0, msg=config.stderr)
