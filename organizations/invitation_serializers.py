from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OrganizationInvitation, OrganizationMembership, Organization

User = get_user_model()


class OrganizationInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=OrganizationMembership.ROLE_CHOICES,
        default=OrganizationMembership.MEMBER,
    )

    def validate_email(self, value):
        return value.lower()


class OrganizationInvitationAcceptSerializer(serializers.Serializer):
    token = serializers.UUIDField()

    def validate(self, data):
        try:
            invite = OrganizationInvitation.objects.select_related(
                "organization"
            ).get(token=data["token"], is_accepted=False)
        except OrganizationInvitation.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used invitation.")

        if invite.is_expired():
            raise serializers.ValidationError("Invitation has expired.")

        data["invite"] = invite
        return data
