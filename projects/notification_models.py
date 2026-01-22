
from django.db import models
from django.conf import settings
from organizations.models import Organization

User = settings.AUTH_USER_MODEL


class Notification(models.Model):
    """
    In-app notification for a user.
    """
    TYPE_CHOICES = [
        ("CARD_MOVED", "Card moved"),
        ("CARD_ASSIGNED", "Card assigned"),
        ("INVITE_ACCEPTED", "Invite accepted"),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    metadata = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["organization"]),
        ]

    def __str__(self):
        return f"{self.type} → {self.recipient}"
