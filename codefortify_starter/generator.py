"""Project generation orchestration."""

from __future__ import annotations

import os
import re
import stat
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from codefortify_starter.constants import (
    BASE_REQUIREMENTS,
    DATABASE_REQUIREMENTS,
    EXECUTABLE_FILES,
    FEATURE_REQUIREMENTS,
    PACKAGE_VERSION,
)
from codefortify_starter.template_engine import TemplateEngine


UNRESOLVED_TOKEN_RE = re.compile(r"(\[\[.+?\]\]|\[%.*?%\])", re.DOTALL)


@dataclass(frozen=True)
class GenerationOptions:
    project_name: str
    project_slug: str
    project_title: str
    project_package: str
    project_class_name: str
    target_root: Path
    database: str
    use_htmx: bool = False
    use_drf: bool = False
    use_docker: bool = False
    use_celery: bool = False
    use_git: bool = True
    force: bool = False
    package_version: str = PACKAGE_VERSION
    created_by: str = "codefortify-starter"

    @property
    def project_path(self) -> Path:
        return self.target_root / self.project_name


@dataclass(frozen=True)
class GenerationResult:
    project_path: Path
    requirements: list[str]
    warnings: list[str] = field(default_factory=list)


class StarterProjectGenerator:
    """Generates starter projects from base and feature template trees."""

    def __init__(self, template_root: Path | None = None) -> None:
        self.template_root = template_root or (Path(__file__).resolve().parent / "templates")
        self.engine = TemplateEngine()

    def generate(self, options: GenerationOptions) -> GenerationResult:
        warnings: list[str] = []
        written_paths: set[Path] = set()
        options.target_root.mkdir(parents=True, exist_ok=True)
        project_path = options.project_path

        if project_path.exists() and not options.force:
            raise FileExistsError(f"Destination '{project_path}' already exists. Use --force to overwrite safely.")
        if project_path.exists() and not project_path.is_dir():
            raise NotADirectoryError(f"Destination '{project_path}' exists and is not a directory.")
        project_path.mkdir(parents=True, exist_ok=True)

        context = self._build_context(options)
        written_paths.update(self._render_base(context, project_path))
        written_paths.update(self._render_feature_overlays(context, project_path, options))

        requirements = self._build_requirements(options)
        written_paths.add(self._write_requirements(project_path, requirements))
        self._assert_no_unresolved_tokens(written_paths)

        if options.use_docker:
            self._set_executable_bits(project_path)
            if options.database == "sqlite":
                warnings.append("Docker + SQLite is supported for development only and is not recommended for production.")

        if options.use_git:
            warning = self._initialize_git(project_path)
            if warning:
                warnings.append(warning)

        return GenerationResult(project_path=project_path, requirements=requirements, warnings=warnings)

    def _render_base(self, context: dict[str, object], project_path: Path) -> set[Path]:
        base_dir = self.template_root / "base_project"
        written_paths = self.engine.render_tree(base_dir, project_path, context)
        (project_path / "media").mkdir(exist_ok=True)
        media_gitkeep = project_path / "media" / ".gitkeep"
        media_gitkeep.touch(exist_ok=True)
        written_paths.add(media_gitkeep)
        return written_paths

    def _render_feature_overlays(
        self,
        context: dict[str, object],
        project_path: Path,
        options: GenerationOptions,
    ) -> set[Path]:
        written_paths: set[Path] = set()
        feature_flags = {
            "htmx": options.use_htmx,
            "drf": options.use_drf,
            "docker": options.use_docker,
            "celery": options.use_celery,
        }
        for feature_name, enabled in feature_flags.items():
            if not enabled:
                continue
            feature_dir = self.template_root / "features" / feature_name
            written_paths.update(self.engine.render_tree(feature_dir, project_path, context))
        return written_paths

    def _build_context(self, options: GenerationOptions) -> dict[str, object]:
        return {
            "project_name": options.project_name,
            "project_slug": options.project_slug,
            "project_title": options.project_title,
            "project_package": options.project_package,
            "project_class_name": options.project_class_name,
            "database": options.database,
            "use_htmx": options.use_htmx,
            "use_drf": options.use_drf,
            "use_docker": options.use_docker,
            "use_celery": options.use_celery,
            "use_postgres": options.database == "postgres",
            "use_mysql": options.database == "mysql",
            "use_sqlite": options.database == "sqlite",
            "use_git": options.use_git,
            "package_version": options.package_version,
            "created_by": options.created_by,
        }

    def _build_requirements(self, options: GenerationOptions) -> list[str]:
        dependencies: list[str] = list(BASE_REQUIREMENTS)

        if options.use_htmx:
            dependencies.extend(FEATURE_REQUIREMENTS["htmx"])
        if options.use_drf:
            dependencies.extend(FEATURE_REQUIREMENTS["drf"])
        if options.use_docker:
            dependencies.extend(FEATURE_REQUIREMENTS["docker"])
        if options.use_celery:
            dependencies.extend(FEATURE_REQUIREMENTS["celery"])

        dependencies.extend(DATABASE_REQUIREMENTS[options.database])

        # Stable dedupe order
        deduped = list(dict.fromkeys(dependencies))
        return deduped

    def _write_requirements(self, project_path: Path, dependencies: list[str]) -> Path:
        requirements_path = project_path / "requirements.txt"
        body = "\n".join(dependencies) + "\n"
        requirements_path.write_text(body, encoding="utf-8")
        return requirements_path

    def _set_executable_bits(self, project_path: Path) -> None:
        for relative_path in EXECUTABLE_FILES:
            file_path = project_path / relative_path
            if not file_path.exists():
                continue
            mode = file_path.stat().st_mode
            file_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def _assert_no_unresolved_tokens(self, paths: set[Path]) -> None:
        for path in sorted(paths):
            if not path.exists() or not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if UNRESOLVED_TOKEN_RE.search(content):
                raise RuntimeError(f"Unresolved template token found in generated file: {path}")

    def _initialize_git(self, project_path: Path) -> str | None:
        try:
            completed = subprocess.run(
                ["git", "init"],
                cwd=project_path,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError:
            return "Git is not installed; skipped repository initialization."

        if completed.returncode != 0:
            message = (completed.stderr or "").strip() or "Unknown git init failure."
            return f"Failed to initialize git repository: {message}"

        # Avoid hard failure if user shell/environment does not support this command.
        subprocess.run(
            ["git", "symbolic-ref", "HEAD", "refs/heads/main"],
            cwd=project_path,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return None


def build_generation_options(
    *,
    project_name: str,
    project_slug: str,
    project_title: str,
    project_package: str,
    project_class_name: str,
    directory: Path,
    database: str,
    use_htmx: bool,
    use_drf: bool,
    use_docker: bool,
    use_celery: bool,
    no_git: bool,
    force: bool,
) -> GenerationOptions:
    created_by = os.environ.get("USER") or os.environ.get("USERNAME") or "codefortify"
    return GenerationOptions(
        project_name=project_name,
        project_slug=project_slug,
        project_title=project_title,
        project_package=project_package,
        project_class_name=project_class_name,
        target_root=directory,
        database=database,
        use_htmx=use_htmx,
        use_drf=use_drf,
        use_docker=use_docker,
        use_celery=use_celery,
        use_git=not no_git,
        force=force,
        created_by=created_by,
    )
