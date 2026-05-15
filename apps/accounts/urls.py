from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from apps.accounts.views import (
    ActivateEmailView,
    PermissionDeniedView,
    ProfileUpdateView,
    ProfileView,
    ResendActivationView,
    UserLoginView,
    UserRegistrationView,
    web_logout,
)


app_name = "accounts"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", web_logout, name="logout"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("activate/<uidb64>/<token>/", ActivateEmailView.as_view(), name="activate"),
    path("email/resend/", ResendActivationView.as_view(), name="resend-activation"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile-edit"),
    path("permission-denied/", PermissionDeniedView.as_view(), name="permission-denied"),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            success_url=reverse_lazy("accounts:password-change-done"),
        ),
        name="password-change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password-change-done",
    ),
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/email/password_reset_email.txt",
            html_email_template_name="accounts/email/password_reset_email.html",
            subject_template_name="accounts/email/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password-reset-done"),
        ),
        name="password-reset",
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password-reset-done",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password-reset-complete"),
        ),
        name="password-reset-confirm",
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password-reset-complete",
    ),
]
