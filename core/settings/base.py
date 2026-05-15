import logging.config
import os
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from app_libs.logger_config import LOGGING
from core.settings.restconf import REST_FRAMEWORK, SIMPLE_JWT


BASE_DIR = Path(__file__).resolve().parent.parent.parent
CORE_DIR = BASE_DIR / "core"
APPS_DIR = BASE_DIR / "apps"

TRUE_VALUES = {"1", "true", "yes", "on"}


def env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


DEBUG = env_flag("DEBUG", default=env_flag("CODEFORTIFY_DEBUG", default=True))
SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("CODEFORTIFY_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-change-me-in-env"
    else:
        raise ImproperlyConfigured("SECRET_KEY is required when DEBUG is False.")

ALLOWED_HOSTS = [
    host.strip()
    for host in (
        os.environ.get("ALLOWED_HOSTS")
        or os.environ.get("CODEFORTIFY_ALLOWED_HOSTS")
        or "localhost,127.0.0.1,0.0.0.0"
    ).split(",")
    if host.strip()
]
if DEBUG:
    for local_host in ("localhost", "127.0.0.1", "0.0.0.0", "testserver"):
        if local_host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(local_host)

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in (
        os.environ.get("CSRF_TRUSTED_ORIGINS")
        or os.environ.get("CODEFORTIFY_CSRF_TRUSTED_ORIGINS")
        or "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    if origin.strip()
]
if DEBUG:
    for local_origin in ("http://localhost:8000", "http://127.0.0.1:8000"):
        if local_origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(local_origin)
CSRF_FAILURE_VIEW = "core.views.csrf_failure"


INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    "django.contrib.postgres",
    "crispy_forms",
    "crispy_bootstrap5",
    "widget_tweaks",
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "apps.accounts",
    "apps.home",
    "base",
]

MIDDLEWARE = [
    "core.middleware.security.SecurityHeadersMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.exceptions.SafeExceptionMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(CORE_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

SITE_ID = 1
SITE_NAME = os.environ.get("SITE_NAME", "CodefortifyAuth")
SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "localhost:8000")

DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()
if not DATABASE_URL:
    postgres_host = os.environ.get("POSTGRES_HOST")
    if postgres_host:
        postgres_port = os.environ.get("POSTGRES_PORT", "5432")
        postgres_db = os.environ.get("POSTGRES_DB", "codefortifyauth")
        postgres_user = os.environ.get("POSTGRES_USER", "postgres")
        postgres_password = os.environ.get("POSTGRES_PASSWORD", "postgres")
        DATABASE_URL = (
            f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
        )
    else:
        sqlite_path = BASE_DIR / "db.sqlite3"
        DATABASE_URL = f"sqlite:///{sqlite_path}"

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=int(os.environ.get("DB_CONN_MAX_AGE", "60")),
        ssl_require=env_flag("DB_SSL_REQUIRE", default=False),
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-us")
TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static_root"
STATICFILES_DIRS = [str(CORE_DIR / "static")]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media_root"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = [
    "apps.accounts.backends.EmailOrUsernameModelBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "accounts:profile"
LOGOUT_REDIRECT_URL = "accounts:login"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

REST_FRAMEWORK = REST_FRAMEWORK
SIMPLE_JWT = SIMPLE_JWT

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@example.com")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_SUBJECT_PREFIX = os.environ.get("EMAIL_SUBJECT_PREFIX", "[CodefortifyAuth] ")

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_flag("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env_flag("EMAIL_USE_SSL", default=False)
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "10"))

ACTIVATION_TOKEN_MAX_AGE_SECONDS = int(os.environ.get("ACTIVATION_TOKEN_MAX_AGE_SECONDS", "259200"))
PASSWORD_RESET_TIMEOUT = int(os.environ.get("PASSWORD_RESET_TIMEOUT", "259200"))

APP_BASE_URL = (os.environ.get("APP_BASE_URL") or os.environ.get("CODEFORTIFY_BASE_URL") or "").strip().rstrip("/")
if not APP_BASE_URL:
    APP_BASE_URL = (os.environ.get("FRONTEND_URL") or os.environ.get("BASE_URL") or "").strip().rstrip("/")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
CELERY_TASK_ALWAYS_EAGER = env_flag("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = env_flag("CELERY_TASK_EAGER_PROPAGATES", default=False)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = USE_TZ

CORS_ALLOW_ALL_ORIGINS = env_flag("CORS_ALLOW_ALL_ORIGINS", default=DEBUG)

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env_flag("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env_flag("CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

LOGGING_CONFIG = None
logging.config.dictConfig(LOGGING)
