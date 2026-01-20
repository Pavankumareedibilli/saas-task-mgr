# projects/activity_views.py
from rest_framework import generics, permissions
from .activity_models import ActivityLog
from .activity_serializers import ActivityLogSerializer


class ActivityLogListAPIView(generics.ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.query_params.get("organization_id")
        if not org_id:
            return ActivityLog.objects.none()

        return ActivityLog.objects.filter(
            organization_id=org_id,
            organization__memberships__user=self.request.user,
            organization__memberships__is_active=True,
        )
