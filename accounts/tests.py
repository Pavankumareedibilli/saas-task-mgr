# accounts/tests.py
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class PasswordResetTests(APITestCase):
    def test_password_reset_flow(self):
        user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="oldpassword123"
        )

        # request reset
        resp = self.client.post(
            "/api/auth/password-reset/request/",
            {"email": "reset@example.com"},
            format="json"
        )
        self.assertEqual(resp.status_code, 200)

        token = user.password_reset_tokens.first().token

        # confirm reset
        resp = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"token": str(token), "new_password": "newpassword123"},
            format="json"
        )
        self.assertEqual(resp.status_code, 200)

        user.refresh_from_db()
        self.assertTrue(user.check_password("newpassword123"))

