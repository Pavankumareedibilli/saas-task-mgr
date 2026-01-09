from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organizations.models import OrganizationInvitation
User = get_user_model()


class OrganizationInviteTests(APITestCase):
    def test_invite_and_accept(self):
        owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="pass12345",
        )
        invitee = User.objects.create_user(
            username="invitee",
            email="invitee@test.com",
            password="pass12345",
        )

        self.client.force_authenticate(owner)
        org = self.client.post("/api/organizations/", {
            "name": "Invite Org",
            "slug": "invite-org"
        }).data

        # send invite
        resp = self.client.post(
            f"/api/organizations/{org['id']}/invite/",
            {"email": "invitee@test.com", "role": "MEMBER"}
        )
        self.assertEqual(resp.status_code, 201)

        token = OrganizationInvitation.objects.first().token

        # accept invite
        self.client.force_authenticate(invitee)
        resp = self.client.post(
            "/api/organizations/invitations/accept/",
            {"token": str(token)}
        )
        self.assertEqual(resp.status_code, 200)
