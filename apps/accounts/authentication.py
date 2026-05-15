from django.contrib.auth import authenticate


def authenticate_by_identifier(request, identifier: str, password: str):
    return authenticate(request=request, username=(identifier or "").strip().lower(), password=password)


def authenticate_by_email(request, email: str, password: str):
    return authenticate_by_identifier(request=request, identifier=email, password=password)
