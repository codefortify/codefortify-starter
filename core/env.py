import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
DOTENV_FILE = ROOT_DIR / ".env"
DOTENV_LOCAL_FILE = ROOT_DIR / ".env.local"
TRUE_VALUES = {"1", "true", "yes", "on"}


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def configure_environment() -> str:
    explicit_environment = (os.environ.get("CODEFORTIFY_ENVIRONMENT") or "").strip().lower()
    load_dotenv_in_production = env_flag("CODEFORTIFY_LOAD_DOTENV_IN_PRODUCTION", default=False)
    should_load_dotenv = explicit_environment != "production" or load_dotenv_in_production

    if should_load_dotenv:
        if DOTENV_LOCAL_FILE.exists() and not env_flag("CODEFORTIFY_SKIP_DOTENV_LOCAL", default=False):
            load_dotenv(DOTENV_LOCAL_FILE)
        if DOTENV_FILE.exists():
            load_dotenv(DOTENV_FILE)

    environment = (os.environ.get("CODEFORTIFY_ENVIRONMENT") or "dev").strip().lower()
    settings_module = "core.settings.production" if environment == "production" else "core.settings.dev"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    return settings_module
