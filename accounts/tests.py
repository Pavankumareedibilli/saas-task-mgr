# accounts/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def test_register_and_login_with_email_and_username(self):
        register_url = "/api/auth/register/"
        token_url = "/api/auth/token/"
        me_url = "/api/auth/accounts/me/"

        # Register
        resp = self.client.post(register_url, {
            "username": "alice",
            "email": "alice@example.com",
            "password": "securepass123",
            "password2": "securepass123"
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(username="alice").exists())

        # Login by username
        resp = self.client.post(token_url, {"username": "alice", "password": "securepass123"}, format="json")
        self.assertEqual(resp.status_code, 200)
        access = resp.data.get("access")
        self.assertIsNotNone(access)

        # Use token to get profile
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = self.client.get(me_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["username"], "alice")

        # Login by email
        self.client.credentials()  # reset
        resp = self.client.post(token_url, {"username": "alice@example.com", "password": "securepass123"}, format="json")
        self.assertEqual(resp.status_code, 200)
