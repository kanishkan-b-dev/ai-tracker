import time

from django.contrib.auth import logout


class AbsoluteSessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            expires_at = request.session.get("auth_expires_at")
            if not isinstance(expires_at, int) or time.time() >= expires_at:
                logout(request)

        return self.get_response(request)
