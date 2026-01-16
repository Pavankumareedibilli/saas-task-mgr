from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organizations.models import Organization

User = get_user_model()


class BoardListCardTests(APITestCase):
    def test_board_list_card_flow(self):
        user = User.objects.create_user(
            username="projuser",
            email="proj@test.com",
            password="pass12345",
        )
        self.client.force_authenticate(user)

        org = Organization.objects.create(
            name="Project Org",
            slug="project-org",
            created_by=user,
        )
        from organizations.models import OrganizationMembership
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role="OWNER",
        )

        board = self.client.post("/api/boards/", {
            "name": "Main Board",
            "organization_id": org.id,
        }).data

        list_obj = self.client.post("/api/lists/", {
            "title": "Todo",
            "board_id": board["id"],
        }).data

        card = self.client.post("/api/cards/", {
            "title": "Initial task",
            "list_id": list_obj["id"],
        })

        self.assertEqual(card.status_code, 201)
