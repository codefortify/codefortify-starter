from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import update_last_login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.email import send_activation_email
from apps.accounts.models import normalize_username_value
from apps.accounts.utils import check_activation_token, decode_uid, encode_uid, make_activation_token


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "password", "password2")
        read_only_fields = ("id",)

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate_username(self, value):
        if not value:
            return ""
        normalized = normalize_username_value(value)
        if User.objects.filter(username__iexact=normalized).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return normalized

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.pop("password2", None)
        if password != password2:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        validate_password(password)
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data.get("username") or None,
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            is_active=False,
            email_verified=False,
        )
        request = self.context.get("request")
        if request is not None:
            send_activation_email(request, user)
        return user


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "email_verified", "is_active")


class CODEFORTIFYTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "identifier"
    identifier = serializers.CharField(required=False, write_only=True)
    email = serializers.CharField(required=False, write_only=True)
    username = serializers.CharField(required=False, write_only=True)
    default_error_messages = {
        "invalid_login": "Please enter a correct email/username and password.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["identifier"].required = False

    def _extract_identifier(self, attrs):
        identifier = attrs.get("identifier") or attrs.get("email") or attrs.get("username")
        if not identifier:
            raise serializers.ValidationError({"identifier": "This field is required."})
        return identifier.strip().lower()

    def validate(self, attrs):
        identifier = self._extract_identifier(attrs)
        attrs[self.username_field] = identifier

        candidate = User.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier)).first()
        if candidate and not candidate.is_active:
            raise serializers.ValidationError("Account is inactive. Verify your email first.")
        if candidate and not candidate.email_verified:
            raise serializers.ValidationError("Email is not verified.")

        self.user = authenticate(
            request=self.context.get("request"),
            username=identifier,
            password=attrs["password"],
            identifier=identifier,
        )
        if self.user is None:
            raise serializers.ValidationError(self.error_messages["invalid_login"])

        refresh = self.get_token(self.user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        data["user"] = UserMeSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        refresh = self.validated_data["refresh"]
        token = RefreshToken(refresh)
        token.blacklist()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()

    def save(self, request):
        form = PasswordResetForm(data={"email": self.validated_data["email"]})
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)
        form.save(
            request=request,
            use_https=request.is_secure(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            email_template_name="accounts/email/password_reset_email.txt",
            subject_template_name="accounts/email/password_reset_subject.txt",
            html_email_template_name="accounts/email/password_reset_email.html",
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password1 = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        password1 = attrs.get("new_password1")
        password2 = attrs.get("new_password2")
        if password1 != password2:
            raise serializers.ValidationError({"new_password2": "Passwords do not match."})

        try:
            user_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=user_id)
        except Exception as exc:
            raise serializers.ValidationError({"uid": "Invalid user identifier."}) from exc

        if not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        validate_password(password1, user=user)
        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        form = SetPasswordForm(
            user=user,
            data={
                "new_password1": self.validated_data["new_password1"],
                "new_password2": self.validated_data["new_password2"],
            },
        )
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)
        form.save()
        return user


class EmailVerifySerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        uid = attrs["uid"]
        token = attrs["token"]
        user_id = decode_uid(uid)
        if not user_id:
            raise serializers.ValidationError({"uid": "Invalid user identifier."})
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError({"uid": "User does not exist."}) from exc
        if not check_activation_token(user, token):
            raise serializers.ValidationError({"token": "Invalid or expired activation token."})
        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.email_verified = True
        user.is_active = True
        user.save(update_fields=["email_verified", "is_active", "updated_at"])
        return user


class EmailResendSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        email = value.strip().lower()
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError("No account found with this email.") from exc
        if user.email_verified:
            raise serializers.ValidationError("Email is already verified.")
        self.user = user
        return email

    def save(self, request):
        send_activation_email(request, self.user)
        return self.user


class ActivationPayloadSerializer(serializers.Serializer):
    uid = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)

    @staticmethod
    def from_user(user):
        return {
            "uid": encode_uid(user),
            "token": make_activation_token(user),
        }
