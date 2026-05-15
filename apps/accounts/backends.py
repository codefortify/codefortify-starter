from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        UserModel = get_user_model()
        identifier = (username or email or kwargs.get("identifier") or "").strip().lower()
        if not identifier or not password:
            return None

        lookup = Q(email__iexact=identifier) | Q(username__iexact=identifier)
        queryset = UserModel.objects.filter(lookup).order_by("id")

        try:
            user = queryset.get()
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            if "@" in identifier:
                user = UserModel.objects.filter(email__iexact=identifier).order_by("id").first()
                if user is None:
                    user = UserModel.objects.filter(username__iexact=identifier).order_by("id").first()
            else:
                user = UserModel.objects.filter(username__iexact=identifier).order_by("id").first()
                if user is None:
                    user = UserModel.objects.filter(email__iexact=identifier).order_by("id").first()
            if user is None:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


class EmailBackend(EmailOrUsernameModelBackend):
    """Backward-compatible alias for older settings."""
