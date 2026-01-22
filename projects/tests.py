from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from organizations.models import Organization
from projects.models import Card,List,Board
User = get_user_model()


from projects.activity_models import ActivityLog

class ActivityLogTests(APITestCase):
    def test_activity_logged_on_card_create(self):
        user = User.objects.create_user(
            username="loguser",
            email="log@test.com",
            password="pass12345",
        )
        self.client.force_authenticate(user)

        from organizations.models import Organization, OrganizationMembership
        org = Organization.objects.create(
            name="Log Org",
            slug="log-org",
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

        self.client.post("/api/cards/", {
            "title": "Logged task",
            "list_id": lst.id,
        })

        self.assertEqual(ActivityLog.objects.count(), 1)



class CardSearchTests(APITestCase):
    def test_search_cards(self):
        user = User.objects.create_user(
            username="searchuser",
            email="search@test.com",
            password="pass12345",
        )
        self.client.force_authenticate(user)

        from organizations.models import Organization, OrganizationMembership
        org = Organization.objects.create(
            name="Search Org",
            slug="search-org",
            created_by=user,
        )
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role="OWNER",
        )

        board = Board.objects.create(
            name="Search Board",
            organization=org,
            created_by=user,
        )
        lst = List.objects.create(board=board, title="Todo", position=1)

        Card.objects.create(
            list=lst,
            title="Fix auth bug",
            position=1,
            created_by=user,
        )
        Card.objects.create(
            list=lst,
            title="Improve search",
            position=2,
            created_by=user,
        )

        resp = self.client.get("/api/card-search/?title=auth")
        self.assertEqual(len(resp.data["results"]), 1)

from unittest.mock import patch
from projects.tasks import send_email_task

class AsyncEmailTests(APITestCase):
    @patch("projects.tasks.send_mail")
    def test_email_task_called(self, mock_send):
        send_email_task(
            subject="Test",
            message="Hello",
            recipient_list=["a@test.com"],
        )
        self.assertTrue(mock_send.called)
from projects.notification_models import Notification

class NotificationTests(APITestCase):
    def test_card_assignment_creates_notification(self):
        user1 = User.objects.create_user(
            username="u1", email="u1@test.com", password="pass12345"
        )
        user2 = User.objects.create_user(
            username="u2", email="u2@test.com", password="pass12345"
        )

        self.client.force_authenticate(user1)

        from organizations.models import Organization, OrganizationMembership
        org = Organization.objects.create(
            name="Notif Org",
            slug="notif-org",
            created_by=user1,
        )
        OrganizationMembership.objects.create(
            user=user1, organization=org, role="OWNER"
        )
        OrganizationMembership.objects.create(
            user=user2, organization=org, role="MEMBER"
        )

        board = Board.objects.create(
            name="Board", organization=org, created_by=user1
        )
        lst = List.objects.create(board=board, title="Todo", position=1)
        card = Card.objects.create(
            list=lst, title="Task", position=1, created_by=user1
        )

        self.client.patch(
            f"/api/cards/{card.id}/assign/",
            {"assignee_id": user2.id},
        )

        self.assertEqual(Notification.objects.count(), 1)
