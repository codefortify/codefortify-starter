from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthAPITests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.active_user = User.objects.create_user(
            email="apiuser@example.com",
            password=self.password,
            is_active=True,
            email_verified=True,
        )
        self.inactive_user = User.objects.create_user(
            email="inactive-api@example.com",
            password=self.password,
            is_active=False,
            email_verified=False,
        )

    def test_api_register(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "newapi@example.com",
                "username": "new_api_user",
                "first_name": "New",
                "last_name": "Api",
                "password": self.password,
                "password2": self.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newapi@example.com").exists())
        self.assertEqual(len(mail.outbox), 1)

    def test_api_duplicate_email_validation(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": self.active_user.email,
                "username": "duplicate_user",
                "password": self.password,
                "password2": self.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_api_token_login(self):
        response = self.client.post(
            "/api/auth/token/",
            {"identifier": self.active_user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_api_token_login_with_username(self):
        response = self.client.post(
            "/api/auth/token/",
            {"identifier": self.active_user.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_api_token_login_with_legacy_email_field(self):
        response = self.client.post(
            "/api/auth/token/",
            {"email": self.active_user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_api_login_endpoint_with_identifier(self):
        response = self.client.post(
            "/api/auth/login/",
            {"identifier": self.active_user.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_api_token_refresh(self):
        token_response = self.client.post(
            "/api/auth/token/",
            {"identifier": self.active_user.email, "password": self.password},
            format="json",
        )
        refresh = token_response.data["refresh"]
        response = self.client.post("/api/auth/token/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_api_me_endpoint(self):
        token_response = self.client.post(
            "/api/auth/token/",
            {"identifier": self.active_user.email, "password": self.password},
            format="json",
        )
        access = token_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.active_user.email)
        self.assertEqual(response.data["username"], self.active_user.username)

    def test_api_inactive_user_behavior(self):
        response = self.client.post(
            "/api/auth/token/",
            {"identifier": self.inactive_user.email, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_invalid_identifier_behavior(self):
        response = self.client.post(
            "/api/auth/token/",
            {"identifier": "missing-user", "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_email_verify_and_resend(self):
        resend_response = self.client.post(
            "/api/auth/email/resend/",
            {"email": self.inactive_user.email},
            format="json",
        )
        self.assertEqual(resend_response.status_code, status.HTTP_200_OK)

        uid = urlsafe_base64_encode(force_bytes(self.inactive_user.pk))
        token = default_token_generator.make_token(self.inactive_user)
        verify_response = self.client.post(
            "/api/auth/email/verify/",
            {"uid": uid, "token": token},
            format="json",
        )
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.email_verified)
        self.assertTrue(self.inactive_user.is_active)

    def test_api_password_reset_and_confirm(self):
        reset_response = self.client.post(
            "/api/auth/password/reset/",
            {"email": self.active_user.email},
            format="json",
        )
        self.assertEqual(reset_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(mail.outbox), 1)

        uid = urlsafe_base64_encode(force_bytes(self.active_user.pk))
        token = default_token_generator.make_token(self.active_user)
        confirm_response = self.client.post(
            "/api/auth/password/reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "new_password1": "UpdatedStrongPass123!",
                "new_password2": "UpdatedStrongPass123!",
            },
            format="json",
        )
        self.assertEqual(confirm_response.status_code, status.HTTP_200_OK)
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password("UpdatedStrongPass123!"))
