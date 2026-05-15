from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.forms import (
    AdminEmailOrUsernameAuthenticationForm,
    UserAdminChangeForm,
    UserAdminCreationForm,
)
from apps.accounts.models import User, UserLog


admin.site.login_form = AdminEmailOrUsernameAuthenticationForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    model = User

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "email_verified",
        "is_staff",
        "is_superuser",
        "is_active",
    )
    list_filter = ("email_verified", "is_staff", "is_superuser", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("username", "email")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Status", {"fields": ("email_verified", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("last_login", "date_joined", "updated_at")}),
    )
    readonly_fields = ("last_login", "date_joined", "updated_at")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__email", "description", "ip_address")
    readonly_fields = ("user", "action", "description", "ip_address", "created_at")
