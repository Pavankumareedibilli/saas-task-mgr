# projects/activity_models.py
from django.db import models
from django.conf import settings
from organizations.models import Organization

User = settings.AUTH_USER_MODEL


class ActivityLog(models.Model):
    """
    Immutable audit log entry.
    """
    ACTION_CHOICES = [
        ("BOARD_CREATED", "Board created"),
        ("BOARD_ARCHIVED", "Board archived"),
        ("BOARD_RESTORED", "Board restored"),

        ("LIST_CREATED", "List created"),
        ("LIST_REORDERED", "List reordered"),
        ("LIST_ARCHIVED", "List archived"),

        ("CARD_CREATED", "Card created"),
        ("CARD_MOVED", "Card moved"),
        ("CARD_REORDERED", "Card reordered"),
        ("CARD_ARCHIVED", "Card archived"),
        ("CARD_RESTORED", "Card restored"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activity_logs",
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)

    # JSONB payload — what exactly happened
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "created_at"]),
        ]

    def __str__(self):
        return f"{self.action} by {self.actor}"
