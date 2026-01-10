# organizations/member_serializers.py
from rest_framework import serializers
from .models import OrganizationMembership


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = (
            "id",
            "user_id",
            "username",
            "email",
            "role",
            "joined_at",
        )


class OrganizationMemberRoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=OrganizationMembership.ROLE_CHOICES)
