import time
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(SESSION_COOKIE_AGE=15 * 60)
class AbsoluteSessionTimeoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="session-user", password="pass1234")

    def test_login_sets_a_fixed_expiration_and_shows_countdown(self):
        response = self.client.post(
            reverse("login"),
            {"username": "session-user", "password": "pass1234"},
        )

        self.assertRedirects(response, reverse("dashboard"), fetch_redirect_response=False)
        expires_at = self.client.session["auth_expires_at"]
        self.assertGreater(expires_at, int(time.time()))
        self.assertLessEqual(expires_at, int(time.time()) + 15 * 60)

        dashboard = self.client.get(reverse("dashboard"))
        self.assertContains(dashboard, 'id="session-countdown"')
        self.assertContains(dashboard, "Your session is about to expire")

    def test_authenticated_requests_do_not_extend_the_login_deadline(self):
        self.client.force_login(self.user)
        session = self.client.session
        session["auth_expires_at"] = 1_000
        session.save()

        with patch("tracker.middleware.time.time", return_value=1_001):
            response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))
        self.assertNotIn("_auth_user_id", self.client.session)

