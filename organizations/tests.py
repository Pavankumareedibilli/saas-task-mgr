from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class OrganizationTests(APITestCase):
    def test_org_creation_and_visibility(self):
        user = User.objects.create_user(
            username="orguser",
            email="org@example.com",
            password="pass12345"
        )

        self.client.force_authenticate(user=user)

        # create org
        resp = self.client.post("/api/organizations/", {
            "name": "Test Org",
            "slug": "test-org"
        })
        self.assertEqual(resp.status_code, 201)

        # list orgs
        resp = self.client.get("/api/organizations/")
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["role"], "OWNER")
