from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organizations.models import Organization
from projects.models import Card,List,Board
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


class ReorderMoveTests(APITestCase):
    def test_card_move_between_lists(self):
        user = User.objects.create_user(
            username="moveuser",
            email="move@test.com",
            password="pass12345",
        )
        self.client.force_authenticate(user)

        from organizations.models import OrganizationMembership, Organization
        org = Organization.objects.create(
            name="Move Org",
            slug="move-org",
            created_by=user,
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role="OWNER",
        )

        board = Board.objects.create(
            name="Board",
            organization=org,
            created_by=user,
        )

        l1 = List.objects.create(board=board, title="L1", position=1)
        l2 = List.objects.create(board=board, title="L2", position=2)

        card = Card.objects.create(
            list=l1,
            title="Task",
            position=1,
            created_by=user,
        )

        resp = self.client.patch(
            f"/api/cards/{card.id}/move/",
            {"target_list_id": l2.id},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)


class BoardDetailTests(APITestCase):
    def test_board_detail_nested(self):
        user = User.objects.create_user(
            username="detailuser",
            email="detail@test.com",
            password="pass12345",
        )
        self.client.force_authenticate(user)

        from organizations.models import Organization, OrganizationMembership
        org = Organization.objects.create(
            name="Detail Org",
            slug="detail-org",
            created_by=user,
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role="OWNER",
        )

        board = Board.objects.create(
            name="Detail Board",
            organization=org,
            created_by=user,
        )

        lst = List.objects.create(board=board, title="Todo", position=1)
        Card.objects.create(list=lst, title="Task A", position=1)
        Card.objects.create(list=lst, title="Task B", position=2)

        resp = self.client.get(f"/api/boards/{board.id}/detail/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["lists"]), 1)
        self.assertEqual(len(resp.data["lists"][0]["cards"]), 2)

class ArchiveTests(APITestCase):
    def test_archive_card(self):
        user = User.objects.create_user(
            username="archuser",
            email="arch@test.com",
            password="pass12345",
        )
        self.client.force_authenticate(user)

        from organizations.models import Organization, OrganizationMembership
        org = Organization.objects.create(
            name="Arch Org",
            slug="arch-org",
            created_by=user,
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role="OWNER",
        )

        board = Board.objects.create(
            name="Board",
            organization=org,
            created_by=user,
        )
        lst = List.objects.create(board=board, title="Todo", position=1)
        card = Card.objects.create(
            list=lst,
            title="Task",
            position=1,
            created_by=user,
        )

        resp = self.client.patch(f"/api/cards/{card.id}/archive/")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f"/api/boards/{board.id}/detail/")
        self.assertEqual(len(resp.data["lists"][0]["cards"]), 0)
