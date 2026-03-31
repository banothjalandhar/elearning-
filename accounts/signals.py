from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .models import UserSession


def _get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_device_name(request):
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    return user_agent[:255]


@receiver(user_logged_in)
def create_user_session(sender, request, user, **kwargs):
    if not request.session.session_key:
        request.session.save()

    UserSession.objects.filter(user=user, is_active=True).exclude(session_key=request.session.session_key).update(
        is_active=False
    )
    UserSession.objects.update_or_create(
        session_key=request.session.session_key,
        defaults={
            "user": user,
            "ip_address": _get_client_ip(request),
            "device": _get_device_name(request),
            "is_active": True,
        },
    )


@receiver(user_logged_out)
def deactivate_user_session(sender, request, user, **kwargs):
    session_key = getattr(request.session, "session_key", None)
    if session_key:
        UserSession.objects.filter(session_key=session_key).update(is_active=False)
