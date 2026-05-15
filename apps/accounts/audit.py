from apps.accounts.models import UserLog


def log_user_action(action, user=None, request=None, description=""):
    ip_address = ""
    if request is not None:
        ip_address = request.META.get("REMOTE_ADDR", "")[:45]
    UserLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        description=description,
        ip_address=ip_address,
    )
