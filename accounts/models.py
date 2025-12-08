from django.contrib.auth.models import AbstractUser
from django.db import models

def profile_upload_path(instance, filename):
   
    return f"profiles/{instance.id}/{filename}"

class User(AbstractUser):
   
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to=profile_upload_path, null=True, blank=True)

   
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username or self.email or f"user-{self.id}"
