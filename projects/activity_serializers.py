# projects/activity_serializers.py
from rest_framework import serializers
from .activity_models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = ActivityLog
        fields = (
            "id",
            "action",
            "actor_email",
            "metadata",
            "created_at",
        )
