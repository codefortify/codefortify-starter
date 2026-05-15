from celery import shared_task
from django.utils import timezone


@shared_task
def healthcheck_task() -> str:
    return f"accounts.healthcheck:{timezone.now().isoformat()}"
