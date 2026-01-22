# projects/notification_serializers.py
from rest_framework import serializers
from .notification_models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "type",
            "metadata",
            "is_read",
            "created_at",
        )
