from rest_framework import serializers
from .models import Organization, OrganizationMembership


class OrganizationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "created_at", "role")

    def get_role(self, obj):
        user = self.context["request"].user
        membership = obj.memberships.filter(user=user).first()
        return membership.role if membership else None


class OrganizationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("name", "slug")

    def create(self, validated_data):
        user = self.context["request"].user

        org = Organization.objects.create(
            created_by=user,
            **validated_data
        )

        # creator becomes OWNER
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role=OrganizationMembership.OWNER,
        )

        return org
