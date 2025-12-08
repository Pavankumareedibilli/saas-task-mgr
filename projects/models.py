from django.db import models
from django.conf import settings
from organizations.models import Organization

class Board(models.Model):
   
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="boards")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
