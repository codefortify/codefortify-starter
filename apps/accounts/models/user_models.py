import re

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


_INVALID_USERNAME_CHARS = re.compile(r"[^a-z0-9_]+")
_MULTIPLE_UNDERSCORES = re.compile(r"_+")


def normalize_username_value(username: str) -> str:
    value = (username or "").strip().lower()
    value = _INVALID_USERNAME_CHARS.sub("_", value)
    value = _MULTIPLE_UNDERSCORES.sub("_", value).strip("_")
    return value or "user"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _username_seed_from_email(self, email: str) -> str:
        local_part = (email or "").split("@", 1)[0]
        return normalize_username_value(local_part or "user")

    def _build_unique_username(self, seed: str, *, exclude_pk=None) -> str:
        base = normalize_username_value(seed)
        max_length = self.model._meta.get_field("username").max_length
        base = base[:max_length] or "user"

        queryset = self.model._default_manager.all()
        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)

        candidate = base
        suffix = 1
        while queryset.filter(username__iexact=candidate).exists():
            suffix_value = f"_{suffix}"
            candidate = f"{base[: max_length - len(suffix_value)]}{suffix_value}"
            suffix += 1
        return candidate

    def _resolve_username(self, email: str, username: str | None) -> str:
        if username is not None and str(username).strip():
            normalized = normalize_username_value(username)
            if self.model._default_manager.filter(username__iexact=normalized).exists():
                raise ValueError("A user with this username already exists.")
            return normalized
        return self._build_unique_username(self._username_seed_from_email(email))

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email).strip().lower()
        username = self._resolve_username(email=email, username=extra_fields.pop("username", None))
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        if password is None:
            raise ValueError("Password is required.")
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if password is None:
            raise ValueError("Superuser must have a password.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_FIELD = "email"
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ("-date_joined",)
        db_table = "accounts_user"

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        if self.username:
            self.username = normalize_username_value(self.username)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email
