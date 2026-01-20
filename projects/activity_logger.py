# projects/activity_logger.py
from .activity_models import ActivityLog


def log_activity(*, organization, actor, action, metadata=None):
    """
    Centralized audit logger.
    Never log directly from views.
    """
    ActivityLog.objects.create(
        organization=organization,
        actor=actor,
        action=action,
        metadata=metadata or {},
    )
