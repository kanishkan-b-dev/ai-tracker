from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tracker.models import JobFolder, JobApplication, LearningEntry


class Command(BaseCommand):
    help = "Seed the database with demo learning entries, folders, and job applications"

    def handle(self, *args, **options):
        # Create or fetch demo user
        demo_user, created = User.objects.get_or_create(username="demo")
        if created:
            demo_user.set_password("demo1234")
            demo_user.email = "demo@example.com"
            demo_user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: demo / demo1234"))
        else:
            self.stdout.write("Demo user already exists: demo / demo1234")

        # Also ensure HEALTHCHECK_ADMIN_USERNAME superuser exists if configured
        from django.conf import settings
        admin_uname = getattr(settings, "HEALTHCHECK_ADMIN_USERNAME", "admin")
        if admin_uname and admin_uname != "demo":
            admin_user, admin_created = User.objects.get_or_create(username=admin_uname)
            if admin_created:
                admin_user.set_password("admin1234")
                admin_user.email = f"{admin_uname}@example.com"
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f"Created healthcheck admin user: {admin_uname} / admin1234"))
            else:
                self.stdout.write(f"Healthcheck admin user already exists: {admin_uname}")

        # Avoid duplicating demo data if already populated
        if JobApplication.objects.filter(user=demo_user).exists() and LearningEntry.objects.filter(user=demo_user).exists():
            self.stdout.write("Demo data already seeded for user 'demo'.")
            return

        today = timezone.localdate()

        # Folders
        folder_linkedin, _ = JobFolder.objects.get_or_create(user=demo_user, name="LinkedIn")
        folder_indeed, _ = JobFolder.objects.get_or_create(user=demo_user, name="Indeed")
        folder_wellfound, _ = JobFolder.objects.get_or_create(user=demo_user, name="Wellfound")

        # Jobs inside LinkedIn folder
        JobApplication.objects.get_or_create(
            user=demo_user,
            folder=folder_linkedin,
            company_name="Deloitte",
            defaults={
                "job_title": "AI Eng",
                "status": "Applied",
                "job_url": "https://southasiacareers.deloitte.com/",
                "application_date": today - timedelta(days=2),
                "notes": "Applied via LinkedIn Easy Apply for AI Engineering role.",
            },
        )

        JobApplication.objects.get_or_create(
            user=demo_user,
            folder=folder_linkedin,
            company_name="Microsoft",
            defaults={
                "job_title": "Software Engineer",
                "status": "Interview",
                "job_url": "https://careers.microsoft.com/",
                "application_date": today - timedelta(days=5),
                "notes": "Technical screening scheduled.",
            },
        )

        # Jobs inside Indeed folder
        JobApplication.objects.get_or_create(
            user=demo_user,
            folder=folder_indeed,
            company_name="Google",
            defaults={
                "job_title": "AI Developer",
                "status": "Rejected",
                "job_url": "https://careers.google.com/",
                "application_date": today - timedelta(days=12),
                "notes": "Applied via Indeed listing.",
            },
        )

        # Jobs inside Wellfound folder
        JobApplication.objects.get_or_create(
            user=demo_user,
            folder=folder_wellfound,
            company_name="Nvidia",
            defaults={
                "job_title": "HPC Operations Engineer",
                "status": "Offer",
                "job_url": "https://nvidia.wd5.myworkdayjobs.com/",
                "application_date": today - timedelta(days=20),
                "notes": "Received offer package.",
            },
        )

        # Learning Entries (from user's dashboard)
        LearningEntry.objects.get_or_create(
            user=demo_user,
            title="GROK-INTERVIEW-PREPARATION-FILE",
            defaults={
                "date": today - timedelta(days=1),
                "notes": "Interview preparation notes, architecture guidelines, and distributed system concepts.",
                "code_snippet": "def optimize_pipeline(records):\n    return [r for r in records if r.is_active]",
                "code_language": "python",
            },
        )

        LearningEntry.objects.get_or_create(
            user=demo_user,
            title="CLAUDE-INTERVIEW-PREPARATION-FILE",
            defaults={
                "date": today - timedelta(days=2),
                "notes": "System design deep dive and LLM agent architecture workflows.",
                "code_snippet": "const client = new OpenAI({ apiKey: process.env.API_KEY });",
                "code_language": "javascript",
            },
        )

        LearningEntry.objects.get_or_create(
            user=demo_user,
            title="GEMINI-INTERVIEW-PREPARATION-FILE",
            defaults={
                "date": today - timedelta(days=3),
                "notes": "Google Gemini technical interview preparation notes and coding patterns.",
                "code_snippet": "async def stream_tokens():\n    async for chunk in response:\n        yield chunk.text",
                "code_language": "python",
            },
        )

        LearningEntry.objects.get_or_create(
            user=demo_user,
            title="CHATGPT-INTERVIEW-PREPARATION-FILE",
            defaults={
                "date": today - timedelta(days=4),
                "notes": "Core prompt engineering, REST APIs, and database indexing strategies.",
                "code_snippet": "SELECT company, role, status FROM tracker_jobapplication WHERE status = 'Interview';",
                "code_language": "sql",
            },
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded demo data with folders and entries!"))
