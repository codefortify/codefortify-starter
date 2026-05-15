from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def encode_uid(user) -> str:
    return urlsafe_base64_encode(force_bytes(user.pk))


def decode_uid(uidb64: str):
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except Exception:
        return None


def make_activation_token(user) -> str:
    return default_token_generator.make_token(user)


def check_activation_token(user, token: str) -> bool:
    return default_token_generator.check_token(user, token)


def build_absolute_uri(request, path: str) -> str:
    base_url = settings.APP_BASE_URL
    if base_url:
        return f"{base_url}{path}"
    return request.build_absolute_uri(path)


def build_activation_link(request, user) -> str:
    uid = encode_uid(user)
    token = make_activation_token(user)
    path = reverse("accounts:activate", kwargs={"uidb64": uid, "token": token})
    return build_absolute_uri(request, path)
