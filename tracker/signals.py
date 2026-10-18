import time

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def set_absolute_session_expiry(sender, request, user, **kwargs):
    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
    request.session["auth_expires_at"] = int(time.time()) + settings.SESSION_COOKIE_AGE
