from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase


User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email="Test@Example.com", password="StrongPass123!")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "test")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_with_explicit_username(self):
        user = User.objects.create_user(email="name@example.com", username="Name.User", password="StrongPass123!")
        self.assertEqual(user.username, "name_user")

    def test_create_superuser(self):
        user = User.objects.create_superuser(email="admin@example.com", password="StrongPass123!")
        self.assertEqual(user.username, "admin")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(email="duplicate@example.com", password="StrongPass123!")
        with self.assertRaises(IntegrityError):
            User.objects.create_user(email="duplicate@example.com", password="StrongPass123!")

    def test_duplicate_username_rejected(self):
        User.objects.create_user(email="first@example.com", username="duplicate_user", password="StrongPass123!")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="second@example.com", username="duplicate_user", password="StrongPass123!")
