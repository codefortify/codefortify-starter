# AGENTS.md

## Project map
- Django 5.2 + DRF auth starter with a custom email-based `accounts.User` model (`apps/accounts/models/user_models.py`).
- Root routing is split by domain: `core/urls.py` mounts `apps.home`, `apps.accounts`, and `apps.accounts.api`.
- Shared utilities live in `base/`; project config, middleware, and error handlers live in `core/`.

## Auth architecture to keep in mind
- Web auth is intentionally separate from API auth:
  - Web flows: `apps/accounts/views.py`, `apps/accounts/urls.py`, templates under `apps/accounts/templates/accounts/`.
  - API flows: `apps/accounts/api/views.py`, `serializers.py`, `urls.py`.
- Login is email-based everywhere. See `apps/accounts/backends.py` and `apps/accounts/forms/users.py` for the normalization pattern (`strip().lower()`).
- Registration starts inactive/unverified; activation is required before login/JWT issuance (`email_verified=False`, `is_active=False`).
- Activation/password-reset links are built with signed tokens and UID helpers in `apps/accounts/utils.py`.

## Code patterns worth preserving
- Prefer re-exported package imports such as `from apps.accounts.models import User, UserLog` and `from apps.accounts.forms import ...`.
- Class-based views generally use `reverse_lazy(...)` for redirects and `LoginRequiredMixin` for protected pages.
- Audit important auth events with `apps/accounts/audit.py::log_user_action()`; it writes to `UserLog` and captures `REMOTE_ADDR` when available.
- In debug mode, registration and resend endpoints may include activation payloads in API responses; production omits them (`apps/accounts/api/views.py`).
- Keep error handling JSON-aware: `core/views.py` and `core/middleware/exceptions.py` return JSON for API/JSON requests and HTML templates otherwise.

## Developer workflows
- Environment bootstrapping happens in `manage.py` via `core.env.configure_environment()`.
- `.env.local` loads before `.env`; `CODEFORTIFY_ENVIRONMENT=production` switches to `core.settings.production`.
- Default local DB is SQLite (`db.sqlite3`) unless `DATABASE_URL` is set.
- Dev email defaults to console backend; activation/reset mail is exercised in tests.

## Commands to run most often
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py makemigrations --check
python manage.py test
python manage.py runserver
```

## Tests and verification focus
- Auth model coverage: `apps/accounts/tests/test_models.py`.
- Web auth flows: `apps/accounts/tests/test_web.py`.
- API auth flows: `apps/accounts/tests/test_api.py`.
- Home page smoke test: `apps/home/tests/test_views.py`.
- When changing auth behavior, update both web and API tests because they intentionally mirror the same lifecycle.

## Project-specific conventions
- Usernames are emails; avoid introducing username-based auth paths.
- Production settings require explicit `SECRET_KEY` and `ALLOWED_HOSTS` (`core/settings/production.py`).
- Security headers are added in middleware, not per-view (`core/middleware/security.py`).
- Static/media roots are configured centrally in `core/settings/base.py`; templates use `core/templates/` as the project-level directory.
