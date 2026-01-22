# projects/notification_logger.py
from .notification_models import Notification


def notify(*, recipient, organization, type, metadata=None):
    """
    Central notification creator.
    """
    Notification.objects.create(
        recipient=recipient,
        organization=organization,
        type=type,
        metadata=metadata or {},
    )
