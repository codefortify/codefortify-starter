from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.accounts.api.serializers import (
    ActivationPayloadSerializer,
    EmailResendSerializer,
    EmailVerifySerializer,
    CODEFORTIFYTokenObtainPairSerializer,
    LogoutSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    UserMeSerializer,
)
from apps.accounts.audit import log_user_action


User = get_user_model()


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(pk=response.data["id"])
        payload = ActivationPayloadSerializer.from_user(user)
        response_data = {
            "message": "Registration successful. Verify your email to activate account.",
            "user": response.data,
            "activation": payload if settings.DEBUG else None,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginAPIView(TokenObtainPairView):
    serializer_class = CODEFORTIFYTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        identifier = (
            request.data.get("identifier")
            or request.data.get("email")
            or request.data.get("username")
            or ""
        )
        identifier = identifier.strip().lower()
        user = User.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier)).first()
        if user:
            log_user_action("login", user=user, request=request)
        return response


class TokenAPIView(TokenObtainPairView):
    serializer_class = CODEFORTIFYTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class TokenRefreshAPIView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_user_action("logout", user=request.user, request=request, description="API logout")
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)


class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)


class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(request=request)
        return Response({"message": "Password reset instructions sent if the email exists."})


class PasswordResetConfirmAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_user_action("password_reset", user=user, request=request)
        return Response({"message": "Password has been reset successfully."})


class EmailVerifyAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_user_action("email_verified", user=user, request=request, description="API email verification")
        return Response({"message": "Email verified successfully."})


class EmailResendAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(request=request)
        return Response(
            {
                "message": "Activation email resent.",
                "activation": {
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                }
                if settings.DEBUG
                else None,
            }
        )
