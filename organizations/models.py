from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL

class Organization(models.Model):

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)  # friendly identifier
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL,
                                   null=True, related_name="created_organizations")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

class OrganizationMembership(models.Model):
    """
    Defines a user's role inside an organization.
    """
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

    ROLE_CHOICES = [
        (OWNER, "Owner"),
        (ADMIN, "Admin"),
        (MEMBER, "Member"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="org_memberships"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("user", "organization")
        indexes = [
            models.Index(fields=["user", "organization"]),
        ]

    def __str__(self):
        return f"{self.user} → {self.organization} ({self.role})"
