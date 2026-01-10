from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organizations.models import OrganizationInvitation
User = get_user_model()


class OrganizationMemberManagementTests(APITestCase):
    def test_member_lifecycle(self):
        owner = User.objects.create_user(
            username="owner2",
            email="owner2@test.com",
            password="pass12345",
        )
        member = User.objects.create_user(
            username="member2",
            email="member2@test.com",
            password="pass12345",
        )

        self.client.force_authenticate(owner)
        org = self.client.post("/api/organizations/", {
            "name": "Members Org",
            "slug": "members-org"
        }).data

        # invite
        self.client.post(
            f"/api/organizations/{org['id']}/invite/",
            {"email": "member2@test.com", "role": "MEMBER"}
        )

        from organizations.models import OrganizationInvitation
        token = OrganizationInvitation.objects.first().token

        self.client.force_authenticate(member)
        self.client.post(
            "/api/organizations/invitations/accept/",
            {"token": str(token)}
        )

        self.client.force_authenticate(owner)

        # list members
        resp = self.client.get(f"/api/organizations/{org['id']}/members/")
        self.assertEqual(len(resp.data), 2)

        # promote member
        member_id = [m["id"] for m in resp.data if m["email"] == "member2@test.com"][0]
        resp = self.client.patch(
            f"/api/organizations/{org['id']}/members/{member_id}/role/",
            {"role": "ADMIN"}
        )
        self.assertEqual(resp.status_code, 200)

