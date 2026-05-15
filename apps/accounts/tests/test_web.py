import re

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from apps.accounts.utils import encode_uid


User = get_user_model()


class WebAuthTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.verified_user = User.objects.create_user(
            email="verified@example.com",
            password=self.password,
            first_name="Verified",
            is_active=True,
            email_verified=True,
        )
        self.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password=self.password,
            is_active=False,
            email_verified=False,
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password=self.password,
            email_verified=True,
        )

    def test_register_view(self):
        response = self.client.post(
            reverse("accounts:register"),
            data={
                "first_name": "New",
                "last_name": "User",
                "username": "new_user",
                "email": "newuser@example.com",
                "password1": self.password,
                "password2": self.password,
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="newuser@example.com")
        self.assertFalse(user.is_active)
        self.assertFalse(user.email_verified)
        self.assertEqual(len(mail.outbox), 1)

    def test_login_view_success(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={"identifier": "verified@example.com", "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:profile"))

    def test_login_view_success_with_username(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={"identifier": self.verified_user.username, "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:profile"))

    def test_login_view_invalid_identifier(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={"identifier": "missing-user", "password": self.password},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct email/username and password.")

    def test_login_view_wrong_password(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={"identifier": "verified@example.com", "password": "WrongPass123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct email/username and password.")

    def test_admin_login_with_email(self):
        response = self.client.post(
            reverse("admin:login"),
            data={"username": self.admin_user.email, "password": self.password, "next": "/admin/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/", response["Location"])

    def test_admin_login_with_username(self):
        response = self.client.post(
            reverse("admin:login"),
            data={"username": self.admin_user.username, "password": self.password, "next": "/admin/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/", response["Location"])

    def test_logout_view(self):
        self.client.force_login(self.verified_user)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:login"))

    def test_permission_behavior_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_email_activation_token_link_generation_and_activation(self):
        uid = encode_uid(self.inactive_user)
        token = default_token_generator.make_token(self.inactive_user)
        response = self.client.get(reverse("accounts:activate", kwargs={"uidb64": uid, "token": token}))
        self.assertEqual(response.status_code, 302)
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.email_verified)
        self.assertTrue(self.inactive_user.is_active)

    def test_resend_activation_flow(self):
        response = self.client.post(
            reverse("accounts:resend-activation"),
            data={"email": self.inactive_user.email},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_flow(self):
        response = self.client.post(
            reverse("accounts:password-reset"),
            data={"email": self.verified_user.email},
        )
        self.assertEqual(response.status_code, 302)
        self.assertGreaterEqual(len(mail.outbox), 1)

        email_body = mail.outbox[-1].body
        match = re.search(r"/accounts/password/reset/confirm/(?P<uid>[^/]+)/(?P<token>[^/]+)/", email_body)
        self.assertIsNotNone(match)
        uid = match.group("uid")
        token = match.group("token")
        confirm_url = reverse("accounts:password-reset-confirm", kwargs={"uidb64": uid, "token": token})
        confirm_get = self.client.get(confirm_url, follow=True)
        self.assertEqual(confirm_get.status_code, 200)
        post_url = confirm_get.request["PATH_INFO"]

        confirm_response = self.client.post(
            post_url,
            data={"new_password1": "NewStrongPass123!", "new_password2": "NewStrongPass123!"},
        )
        self.assertEqual(confirm_response.status_code, 302)
        self.verified_user.refresh_from_db()
        self.assertTrue(self.verified_user.check_password("NewStrongPass123!"))

    def test_basic_template_rendering(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertTemplateUsed(response, "accounts/login.html")
        response = self.client.get(reverse("accounts:register"))
        self.assertTemplateUsed(response, "accounts/registration.html")
        response = self.client.get(reverse("home:home"))
        self.assertTemplateUsed(response, "home/home.html")

    def test_url_reverses(self):
        self.assertEqual(reverse("accounts:login"), "/accounts/login/")
        self.assertEqual(reverse("accounts:register"), "/accounts/register/")
        self.assertEqual(reverse("api_auth:register"), "/api/auth/register/")
