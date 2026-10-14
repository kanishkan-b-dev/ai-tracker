import os
import sys
from urllib import request as urllib_request
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.contrib.auth.models import User
from django.conf import settings
from tracker.supabase_client import is_supabase_configured


class Command(BaseCommand):
    help = "Run system health check and uptime ping verification"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ensure-admin",
            action="store_true",
            help="Ensure the HEALTHCHECK_ADMIN_USERNAME user exists in database",
        )
        parser.add_argument(
            "--ping",
            action="store_true",
            help="Send HTTP GET ping to HEALTHCHECK_APPLICATION_URL to keep Render instance awake",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== System Health Diagnostics ==="))

        # 1. Database Check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
            self.stdout.write(self.style.SUCCESS("[OK] Database connection active."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[FAIL] Database connection failed: {e}"))

        # 2. Redis / Cache Check
        try:
            cache.set("__cli_hc__", "ok", 10)
            if cache.get("__cli_hc__") == "ok":
                backend_name = settings.CACHES["default"]["BACKEND"].split(".")[-1]
                self.stdout.write(self.style.SUCCESS(f"[OK] Cache backend active ({backend_name})."))
            else:
                self.stdout.write(self.style.WARNING("[WARN] Cache read back unexpected value."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[FAIL] Cache connection error: {e}"))

        # 3. Admin User Check
        admin_uname = getattr(settings, "HEALTHCHECK_ADMIN_USERNAME", "admin")
        if admin_uname:
            admin_user = User.objects.filter(username=admin_uname).first()
            if admin_user:
                self.stdout.write(self.style.SUCCESS(f"[OK] Healthcheck admin user '{admin_uname}' exists."))
            else:
                if options.get("ensure_admin"):
                    temp_pass = os.environ.get("HEALTHCHECK_ADMIN_PASSWORD", "AdminPass123!")
                    User.objects.create_superuser(username=admin_uname, email="admin@example.com", password=temp_pass)
                    self.stdout.write(self.style.SUCCESS(f"[CREATED] Superuser '{admin_uname}' created successfully."))
                else:
                    self.stdout.write(self.style.WARNING(f"[NOTICE] Admin user '{admin_uname}' does not exist yet. Run with --ensure-admin to create."))

        # 4. Supabase Storage Check
        if is_supabase_configured():
            bucket = getattr(settings, "SUPABASE_STORAGE_BUCKET", "resumes")
            self.stdout.write(self.style.SUCCESS(f"[OK] Supabase Storage configured (Bucket: '{bucket}')."))
        else:
            self.stdout.write(self.style.NOTICE("[INFO] Supabase Storage not configured (Local storage active)."))

        # 5. App URL & Keep-Alive Ping
        app_url = getattr(settings, "HEALTHCHECK_APPLICATION_URL", "")
        if app_url:
            self.stdout.write(f"Application URL: {app_url}")
            if options.get("ping"):
                target = f"{app_url.rstrip('/')}/health/"
                try:
                    req = urllib_request.Request(target, headers={"User-Agent": "JobTrack-HealthCheck/1.0"})
                    with urllib_request.urlopen(req, timeout=10) as resp:
                        if resp.status == 200:
                            self.stdout.write(self.style.SUCCESS(f"[OK] Successfully pinged {target} (Status: 200 OK)"))
                        else:
                            self.stdout.write(self.style.WARNING(f"[WARN] Ping returned status: {resp.status}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"[FAIL] Failed to ping {target}: {e}"))

        self.stdout.write(self.style.SUCCESS("Health check completed."))
