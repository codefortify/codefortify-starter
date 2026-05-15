from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q

from apps.accounts.models import User, normalize_username_value


class IdentifierAuthenticationForm(forms.Form):
    identifier = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "autocomplete": "username",
                "placeholder": "Enter your email or username",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    error_messages = {
        "invalid_login": "Please enter a correct email/username and password.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean_identifier(self):
        return self.cleaned_data["identifier"].strip().lower()

    def _lookup_user(self, identifier: str):
        return User.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier)).first()

    def clean(self):
        identifier = self.cleaned_data.get("identifier")
        password = self.cleaned_data.get("password")
        if identifier and password:
            candidate = self._lookup_user(identifier)
            if candidate and not candidate.is_active:
                raise forms.ValidationError("This account is inactive. Verify your email first.")
            if candidate and not candidate.email_verified:
                raise forms.ValidationError("This account is not verified yet.")
            self.user_cache = authenticate(self.request, username=identifier, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.error_messages["invalid_login"])
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


EmailAuthenticationForm = IdentifierAuthenticationForm


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        required=False,
        max_length=150,
        help_text="Optional. Leave blank to auto-generate from your email.",
    )
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email")

    def clean_username(self):
        raw_username = self.cleaned_data.get("username", "")
        if not raw_username:
            return ""
        normalized = normalize_username_value(raw_username)
        if User.objects.filter(username__iexact=normalized).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return normalized

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        if password1:
            validate_password(password1)
        return cleaned_data

    def save(self, commit=True):
        if not commit:
            raise ValueError("UserRegistrationForm.save requires commit=True.")
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            username=self.cleaned_data.get("username") or None,
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data.get("first_name", ""),
            last_name=self.cleaned_data.get("last_name", ""),
            is_active=False,
            email_verified=False,
        )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class ResendActivationForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as exc:
            raise forms.ValidationError("No account found with this email.") from exc
        if user.email_verified:
            raise forms.ValidationError("This account is already verified.")
        self.user = user
        return email
