from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from apps.accounts.models import User, normalize_username_value


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name", "is_staff", "is_superuser", "is_active")

    def clean_username(self):
        raw_username = self.cleaned_data.get("username", "")
        if not raw_username:
            return ""
        normalized = normalize_username_value(raw_username)
        if User.objects.filter(username__iexact=normalized).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return normalized

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        if not commit:
            raise ValueError("UserAdminCreationForm.save requires commit=True.")
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            username=self.cleaned_data.get("username") or None,
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
            is_staff=self.cleaned_data.get("is_staff", False),
            is_superuser=self.cleaned_data.get("is_superuser", False),
            is_active=self.cleaned_data.get("is_active", True),
        )


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "email_verified",
        )

    def clean_password(self):
        return self.initial["password"]


class AdminEmailOrUsernameAuthenticationForm(AdminAuthenticationForm):
    username = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(attrs={"autofocus": True}),
    )
