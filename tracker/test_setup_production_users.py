from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings


class SetupProductionUsersTests(TestCase):
    @override_settings(RENDER_USERS="Preetha:test-password:user")
    def test_preetha_is_admin_when_configured_in_render_users(self):
        call_command("setup_production_users", keep_others=True, stdout=StringIO())

        preetha = User.objects.get(username__iexact="preetha")
        self.assertTrue(preetha.is_staff)
        self.assertTrue(preetha.is_superuser)

    @override_settings(
        RENDER_USERS="",
        USER_1_USERNAME="kanishkan",
        USER_1_PASSWORD="test-password",
        USER_2_USERNAME="preetha",
        USER_2_PASSWORD="test-password",
    )
    def test_preetha_is_admin_when_configured_with_individual_variables(self):
        call_command("setup_production_users", keep_others=True, stdout=StringIO())

        preetha = User.objects.get(username="preetha")
        self.assertTrue(preetha.is_staff)
        self.assertTrue(preetha.is_superuser)
