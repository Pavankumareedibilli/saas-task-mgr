# from django.db import models
# from django.conf import settings
# from organizations.models import Organization

# class Board(models.Model):
   
#     org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="boards")
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title

# projects/models.py
from django.db import models
from django.conf import settings
from organizations.models import Organization
from .activity_models import ActivityLog
from .notification_models import Notification

User = settings.AUTH_USER_MODEL


class Board(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="boards",
    )
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class List(models.Model):
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="lists",
    )
    title = models.CharField(max_length=255)
    position = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.title


class Card(models.Model):
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    position = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_cards",
    )

    class Meta:
        ordering = ["position"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title
