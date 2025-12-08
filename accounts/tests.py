from django.test import TestCase
from .models import User

class UserModelTest(TestCase):
    def test_create_user(self):
        u = User.objects.create_user(username="testuser", password="pass1234")
        self.assertTrue(u.pk)
        self.assertTrue(u.check_password("pass1234"))
