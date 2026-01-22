# projects/notification_views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from .notification_models import Notification
from .notification_serializers import NotificationSerializer


class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        )


class NotificationMarkReadAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        if notification.recipient != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        notification.is_read = True
        notification.save()
        return Response({"detail": "Marked as read"})
