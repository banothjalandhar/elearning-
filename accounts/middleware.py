from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

from .models import UserSession


class SingleDeviceSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_path_prefixes = (
            "/admin/",
            "/accounts/",
            "/login/",
            "/logout/",
            "/signup/",
            "/forgot-password/",
            "/verify-otp/",
            "/reset-password/",
            "/static/",
            "/media/",
        )

    def __call__(self, request):
        if request.user.is_authenticated and not self._is_exempt_request(request):
            session_key = getattr(request.session, "session_key", None)
            if not session_key:
                return self.get_response(request)

            active_session = UserSession.objects.filter(
                user=request.user,
                session_key=session_key,
                is_active=True,
            ).first()
            if active_session is None:
                has_other_active_session = UserSession.objects.filter(user=request.user, is_active=True).exclude(
                    session_key=session_key
                ).exists()
                if has_other_active_session:
                    logout(request)
                    messages.error(
                        request,
                        "Your session is no longer active. Please contact admin.",
                        fail_silently=True,
                    )
                    return redirect(reverse("login"))

        return self.get_response(request)

    def _is_exempt_request(self, request):
        return request.path.startswith(self.exempt_path_prefixes)
