from django.conf import settings
from django.db import models
from django.utils import timezone


class UserLog(models.Model):
    class Action(models.TextChoices):
        REGISTER = "register", "Register"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        PASSWORD_RESET = "password_reset", "Password Reset"
        EMAIL_VERIFIED = "email_verified", "Email Verified"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="logs",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=40, choices=Action.choices)
    description = models.CharField(max_length=255, blank=True, default="")
    ip_address = models.CharField(max_length=45, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        db_table = "accounts_user_log"
        ordering = ("-created_at", "-id")

    def __str__(self):
        actor = self.user.email if self.user else "anonymous"
        return f"{actor} - {self.action}"
