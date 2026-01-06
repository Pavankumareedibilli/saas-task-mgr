# accounts/password_reset_serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PasswordResetToken

User = get_user_model()


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value.lower()).exists():
            # IMPORTANT: do NOT reveal whether email exists
            # Security best practice
            return value.lower()
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(min_length=8)

    def validate(self, data):
        try:
            token_obj = PasswordResetToken.objects.select_related("user").get(
                token=data["token"],
                is_used=False
            )
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired token.")

        if token_obj.is_expired():
            raise serializers.ValidationError("Token has expired.")

        data["token_obj"] = token_obj
        return data
