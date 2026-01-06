from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Organization
from .serializers import OrganizationSerializer, OrganizationCreateSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only organizations where user is a member
        return Organization.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True
        ).distinct()

    def get_serializer_class(self):
        if self.action == "create":
            return OrganizationCreateSerializer
        return OrganizationSerializer

    def perform_create(self, serializer):
        serializer.save()
