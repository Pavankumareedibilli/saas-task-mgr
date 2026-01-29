from rest_framework import serializers
from .models import Organization, OrganizationMembership
from django.utils.text import slugify
import uuid

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
    slug = serializers.CharField(required=False)

    class Meta:
        model = Organization
        fields = ("id","name", "slug")

    def create(self, validated_data):
        user = self.context["request"].user

        base_slug = slugify(validated_data["name"])
        slug = base_slug
        if Organization.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

        validated_data["slug"] = slug


        org = Organization.objects.create(
            created_by=user,
            **validated_data
        )

        # Here the one who creates the organization will become the default owner
        OrganizationMembership.objects.create(
            user=user,
            organization=org,
            role=OrganizationMembership.OWNER,
        )

        return org
