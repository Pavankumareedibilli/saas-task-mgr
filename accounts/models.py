from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

def profile_upload_path(instance, filename):
   
    return f"profiles/{instance.id}/{filename}"

class User(AbstractUser):
   
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to=profile_upload_path, null=True, blank=True)

    email = models.EmailField(unique=True)
    bio = models.TextField(null=True, blank=True)
    def save(self, *args, **kwargs):
        # normalize email to lowercase before saving
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username or self.email or f"user-{self.id}"
class PasswordResetToken(models.Model):
    """
    One-time password reset token.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
        ]

    def is_expired(self):
        """
        Token is valid for 15 minutes.
        """
        return timezone.now() > self.created_at + timedelta(minutes=15)

    def __str__(self):
        return f"PasswordResetToken(user={self.user_id}, used={self.is_used})"