"""CLI entry point for project generation."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from codefortify_starter.generator import StarterProjectGenerator, build_generation_options
from codefortify_starter.validators import ValidationError, build_project_identity, normalize_database


console = Console()


def run(
    project_name: str = typer.Argument(..., help="Project directory name to create."),
    htmx: bool = typer.Option(False, "--htmx", help="Include HTMX integration."),
    drf: bool = typer.Option(False, "--drf", help="Include Django REST Framework starter API."),
    docker: bool = typer.Option(False, "--docker", help="Include Docker and Compose files."),
    celery: bool = typer.Option(False, "--celery", help="Include Celery + Redis task setup."),
    database: str | None = typer.Option(
        None,
        "--database",
        help="Database backend to configure: sqlite, postgres, or mysql.",
    ),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git repository initialization."),
    force: bool = typer.Option(False, "--force", help="Allow generation into an existing directory."),
    directory: Path = typer.Option(Path("."), "--directory", help="Parent directory for the generated project."),
    all_features: bool = typer.Option(
        False,
        "--all",
        help="Enable full-stack preset: --htmx --drf --docker --celery --database postgres.",
    ),
) -> None:
    """Generate a Django starter project."""
    try:
        if all_features:
            htmx = True
            drf = True
            docker = True
            celery = True
            if database is None:
                database = "postgres"

        resolved_database = normalize_database(database, use_docker=docker)
        identity = build_project_identity(project_name)

        options = build_generation_options(
            project_name=identity.project_name,
            project_slug=identity.project_slug,
            project_title=identity.project_title,
            project_package=identity.project_package,
            project_class_name=identity.project_class_name,
            directory=directory.resolve(),
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
    except (ValidationError, FileExistsError, NotADirectoryError, RuntimeError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    selected_features = []
    if htmx:
        selected_features.append("htmx")
    if drf:
        selected_features.append("drf")
    if docker:
        selected_features.append("docker")
    if celery:
        selected_features.append("celery")
    features_text = ", ".join(selected_features) if selected_features else "base"

    console.print(
        f"[bold green]Created[/bold green] {result.project_path} "
        f"(database={resolved_database}, features={features_text})"
    )
    if result.warnings:
        for warning in result.warnings:
            console.print(f"[yellow]Warning:[/yellow] {warning}")

    console.print("Next steps:")
    console.print(f"  1. cd {result.project_path}")
    console.print("  2. python -m venv .venv && source .venv/bin/activate")
    console.print("  3. pip install -r requirements.txt")
    console.print("  4. cp .env.example .env")
    console.print("  5. python manage.py migrate && python manage.py runserver")


def main() -> None:
    typer.run(run)


if __name__ == "__main__":
    main()
