from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView
from django.views.generic.edit import CreateView

from apps.accounts.audit import log_user_action
from apps.accounts.email import send_activation_email, send_welcome_email
from apps.accounts.forms import (
    IdentifierAuthenticationForm,
    ProfileUpdateForm,
    ResendActivationForm,
    UserRegistrationForm,
)
from apps.accounts.models import User
from apps.accounts.utils import check_activation_token, decode_uid


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = IdentifierAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not user.email_verified:
            messages.error(self.request, "Your account is not verified. Check your email.")
            return redirect("accounts:resend-activation")
        log_user_action("login", user=user, request=self.request)
        return super().form_valid(form)

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy("accounts:profile")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")
    http_method_names = ["get", "post", "options"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            log_user_action("logout", user=request.user, request=request)
        return super().dispatch(request, *args, **kwargs)


class UserRegistrationView(CreateView):
    form_class = UserRegistrationForm
    template_name = "accounts/registration.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        send_activation_email(self.request, self.object)
        log_user_action("register", user=self.object, request=self.request)
        messages.success(
            self.request,
            "Registration successful. Please check your email to activate your account.",
        )
        return response


class ActivateEmailView(View):
    def get(self, request, uidb64, token):
        user_id = decode_uid(uidb64)
        user = get_object_or_404(User, pk=user_id)
        if check_activation_token(user, token):
            user.email_verified = True
            user.is_active = True
            user.save(update_fields=["email_verified", "is_active", "updated_at"])
            try:
                send_welcome_email(user)
            except Exception:
                pass
            log_user_action("email_verified", user=user, request=request)
            messages.success(request, "Your email has been verified. You can now log in.")
            return redirect("accounts:login")
        messages.error(request, "Activation link is invalid or expired.")
        return redirect("accounts:resend-activation")


class ResendActivationView(FormView):
    form_class = ResendActivationForm
    template_name = "accounts/resend_activation.html"
    success_url = reverse_lazy("accounts:resend-activation")

    def form_valid(self, form):
        send_activation_email(self.request, form.user)
        messages.success(self.request, "Activation email sent again.")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile_update.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)


class PermissionDeniedView(TemplateView):
    template_name = "accounts/permission_denied.html"


def web_logout(request):
    if request.user.is_authenticated:
        log_user_action("logout", user=request.user, request=request)
    logout(request)
    return redirect("accounts:login")
