"""Filesystem + Jinja template rendering utilities."""

from __future__ import annotations

import shutil
from pathlib import Path

from jinja2 import Environment, StrictUndefined


class TemplateEngine:
    """Renders template trees using custom Jinja delimiters."""

    def __init__(self) -> None:
        self._environment = Environment(
            autoescape=False,
            keep_trailing_newline=True,
            trim_blocks=False,
            lstrip_blocks=False,
            undefined=StrictUndefined,
            variable_start_string="[[",
            variable_end_string="]]",
            block_start_string="[%",  # avoids collision with Django template tags
            block_end_string="%]",
        )

    def render_tree(self, source_root: Path, destination_root: Path, context: dict[str, object]) -> set[Path]:
        """Render files from `source_root` into `destination_root`."""
        written_paths: set[Path] = set()
        if not source_root.exists():
            return written_paths

        for source_path in sorted(source_root.rglob("*")):
            relative = source_path.relative_to(source_root)
            destination_path = destination_root / self._normalized_relative_path(relative)
            if source_path.is_dir():
                destination_path.mkdir(parents=True, exist_ok=True)
                continue

            destination_path.parent.mkdir(parents=True, exist_ok=True)
            if source_path.suffix == ".jinja":
                rendered = self.render_text(source_path.read_text(encoding="utf-8"), context)
                destination_path.write_text(rendered, encoding="utf-8")
            else:
                shutil.copy2(source_path, destination_path)
            written_paths.add(destination_path)

        return written_paths

    def render_text(self, template_source: str, context: dict[str, object]) -> str:
        template = self._environment.from_string(template_source)
        return template.render(**context)

    def _normalized_relative_path(self, relative_path: Path) -> Path:
        parts = []
        for part in relative_path.parts:
            normalized = part
            if normalized.startswith("dot-"):
                normalized = f".{normalized[4:]}"
            if normalized.endswith(".jinja"):
                normalized = normalized[: -len(".jinja")]
            parts.append(normalized)
        return Path(*parts)
