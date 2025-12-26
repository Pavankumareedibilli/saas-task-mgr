# accounts/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UniqueEmailTests(APITestCase):
    def test_duplicate_email_registration_fails(self):
        url = "/api/auth/register/"

        payload = {
            "username": "user1",
            "email": "test@example.com",
            "password": "securepass123",
            "password2": "securepass123"
        }

        self.client.post(url, payload, format="json")

        payload["username"] = "user2"
        resp = self.client.post(url, payload, format="json")

        self.assertEqual(resp.status_code, 400)
        self.assertIn("email", resp.data)
