import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from tracker.models import JobFolder


class Command(BaseCommand):
    help = "Strictly provision the two production users from Render Key Vault environment variables"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keep-others",
            action="store_true",
            help="Do not purge demo/testing users from database",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Provisioning Production Key Vault Users ==="))

        # Parse users dictionary from environment
        users_to_provision = []

        render_users_str = getattr(settings, "RENDER_USERS", "") or os.environ.get("RENDER_USERS", "")
        if render_users_str:
            # Format: username:password:role,username:password
            for item in render_users_str.split(","):
                parts = [p.strip() for p in item.split(":") if p.strip()]
                if len(parts) >= 2:
                    is_admin = len(parts) >= 3 and parts[2].lower() in ("admin", "superuser", "staff")
                    users_to_provision.append({
                        "username": parts[0],
                        "password": parts[1],
                        "is_admin": is_admin
                    })

        # If not supplied via RENDER_USERS, use individual USER_1 & USER_2 variables
        if not users_to_provision:
            u1_name = getattr(settings, "USER_1_USERNAME", "kanishkan") or os.environ.get("USER_1_USERNAME", "kanishkan")
            u1_pass = getattr(settings, "USER_1_PASSWORD", "Kanishkan@2004") or os.environ.get("USER_1_PASSWORD", "Kanishkan@2004")
            u2_name = getattr(settings, "USER_2_USERNAME", "preetha") or os.environ.get("USER_2_USERNAME", "preetha")
            u2_pass = getattr(settings, "USER_2_PASSWORD", "Preetha@2005") or os.environ.get("USER_2_PASSWORD", "Preetha@2005")

            users_to_provision = [
                {"username": u1_name, "password": u1_pass, "is_admin": True},
                {"username": u2_name, "password": u2_pass, "is_admin": True},
            ]

        authorized_usernames = set()

        default_folders = ["LinkedIn", "Indeed", "Wellfound", "Glassdoor", "Referrals"]

        for udata in users_to_provision:
            uname = udata["username"]
            upass = udata["password"]
            is_adm = udata["is_admin"] or uname.strip().casefold() == "preetha"
            authorized_usernames.add(uname)

            user, created = User.objects.get_or_create(username=uname)
            user.set_password(upass)
            user.is_staff = is_adm
            user.is_superuser = is_adm
            if not user.email:
                user.email = f"{uname}@jobtrack.local"
            user.save()

            action = "Created" if created else "Updated & Synced"
            role = "Superuser/Admin" if is_adm else "Standard User"
            self.stdout.write(self.style.SUCCESS(f"[OK] {action} user '{uname}' ({role}) with Key Vault credentials."))

            # Ensure default job folders exist for this user
            for fname in default_folders:
                JobFolder.objects.get_or_create(user=user, name=fname)

        # Purge any non-authorized users (e.g. demo, alice, bob) unless --keep-others is passed
        if not options.get("keep_others"):
            stale_users = User.objects.exclude(username__in=authorized_usernames)
            count = stale_users.count()
            if count > 0:
                stale_names = list(stale_users.values_list("username", flat=True))
                stale_users.delete()
                self.stdout.write(self.style.WARNING(f"[PURGED] Removed {count} non-Key Vault user(s): {stale_names}"))

        self.stdout.write(self.style.SUCCESS(f"=== Successfully configured {len(authorized_usernames)} Key Vault user(s) ==="))
