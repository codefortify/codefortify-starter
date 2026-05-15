# CodefortifyAuth Structure

```text
codefortifyauth/
├── .env
├── .env.example
├── .gitignore
├── GeoLite2City/
├── README.md
├── app_libs/
│   ├── error_codes.py
│   └── logger_config.py
├── app_logs/
├── apps/
│   ├── __init__.py
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── api/
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── apps.py
│   │   ├── audit.py
│   │   ├── authentication.py
│   │   ├── backends.py
│   │   ├── email.py
│   │   ├── forms/
│   │   │   ├── admin.py
│   │   │   └── users.py
│   │   ├── migrations/
│   │   ├── models/
│   │   │   ├── user_logs.py
│   │   │   └── user_models.py
│   │   ├── templates/
│   │   │   └── accounts/
│   │   │       ├── email/
│   │   │       ├── login.html
│   │   │       ├── profile.html
│   │   │       ├── registration.html
│   │   │       └── ...
│   │   ├── tests/
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   └── home/
│       ├── admin.py
│       ├── apps.py
│       ├── migrations/
│       ├── models.py
│       ├── templates/home/home.html
│       ├── tests/
│       ├── urls.py
│       └── views.py
├── base/
│   ├── __init__.py
│   ├── apps.py
│   ├── choose.py
│   ├── migrations/
│   ├── models.py
│   ├── search.py
│   ├── utils.py
│   ├── validators.py
│   └── views.py
├── core/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── decorators.py
│   ├── env.py
│   ├── middleware/
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── mixins.py
│   ├── sanitizers.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── production.py
│   │   └── restconf/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       └── pagination.py
│   ├── static/
│   │   ├── assets/
│   │   └── images/
│   ├── templates/
│   │   ├── base/
│   │   ├── base.html
│   │   └── errors/
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   └── wsgi.py
├── db.sqlite3
├── manage.py
├── requirements.txt
└── structure.md
```
