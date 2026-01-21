# projects/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3})
def send_email_task(self, subject, message, recipient_list):
    """
    Async email sender with retry.
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
    )
