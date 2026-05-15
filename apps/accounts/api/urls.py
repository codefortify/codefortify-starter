from django.urls import path

from apps.accounts.api.views import (
    EmailResendAPIView,
    EmailVerifyAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    PasswordResetAPIView,
    PasswordResetConfirmAPIView,
    RegisterAPIView,
    TokenAPIView,
    TokenRefreshAPIView,
)


app_name = "api_auth"

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("token/", TokenAPIView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("me/", MeAPIView.as_view(), name="me"),
    path("password/reset/", PasswordResetAPIView.as_view(), name="password-reset"),
    path("password/reset/confirm/", PasswordResetConfirmAPIView.as_view(), name="password-reset-confirm"),
    path("email/verify/", EmailVerifyAPIView.as_view(), name="email-verify"),
    path("email/resend/", EmailResendAPIView.as_view(), name="email-resend"),
]
