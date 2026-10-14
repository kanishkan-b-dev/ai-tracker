from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from tracker.models import JobFolder, JobApplication, LearningEntry


class TrackerTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="alice", password="password123")
        self.user2 = User.objects.create_user(username="bob", password="password123")

        # Create folder and job for user1
        self.folder_linkedin = JobFolder.objects.create(user=self.user1, name="LinkedIn")
        self.job1 = JobApplication.objects.create(
            user=self.user1,
            folder=self.folder_linkedin,
            company_name="Deloitte",
            job_title="AI Engineer",
            job_url="https://deloitte.com",
            status="Applied",
        )

        # Create entry for user1
        self.entry1 = LearningEntry.objects.create(
            user=self.user1,
            title="Python Testing",
            notes="Wrote unit tests for Django views",
            code_snippet="def test(): pass",
            code_language="python",
        )

    def test_login_flow(self):
        res = self.client.post(
            reverse("login"),
            {"username": "alice", "password": "password123"},
        )
        self.assertEqual(res.status_code, 302)
        self.assertIn("/dashboard/", res.url)

    def test_dashboard_renders(self):
        self.client.login(username="alice", password="password123")
        res = self.client.get(reverse("dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Welcome back, alice!")
        self.assertContains(res, "Deloitte")
        self.assertContains(res, "AI Engineer")
        self.assertContains(res, "LinkedIn")

    def test_jobs_view_shows_folders_and_jobs(self):
        self.client.login(username="alice", password="password123")
        res = self.client.get(reverse("my_jobs"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "LinkedIn")
        self.assertContains(res, "Deloitte")
        self.assertContains(res, "AI Engineer")

    def test_quick_add_folder_workflow(self):
        self.client.login(username="alice", password="password123")
        # User types "Indeed" and hits Okay
        res = self.client.post(
            reverse("quick_add_folder"),
            {"app_name": "Indeed"},
        )
        self.assertEqual(res.status_code, 302)
        indeed_folder = JobFolder.objects.filter(user=self.user1, name="Indeed").first()
        self.assertIsNotNone(indeed_folder)
        self.assertIn(f"/my-jobs/?folder={indeed_folder.pk}", res.url)

        # Now user fills in company name, role, url, status
        create_res = self.client.post(
            reverse("job_create"),
            {
                "company_name": "Microsoft",
                "job_title": "Software Engineer",
                "job_url": "https://microsoft.com",
                "status": "Interview",
                "application_date": "2026-10-13",
                "folder": indeed_folder.pk,
            },
        )
        self.assertEqual(create_res.status_code, 302)
        new_job = JobApplication.objects.filter(user=self.user1, company_name="Microsoft").first()
        self.assertIsNotNone(new_job)
        self.assertEqual(new_job.folder, indeed_folder)
        self.assertEqual(new_job.status, "Interview")

    def test_job_edit_and_delete(self):
        self.client.login(username="alice", password="password123")
        edit_res = self.client.post(
            reverse("job_edit", kwargs={"pk": self.job1.pk}),
            {
                "company_name": "Deloitte Digital",
                "job_title": "Senior AI Engineer",
                "status": "Offer",
                "application_date": "2026-10-13",
                "folder": self.folder_linkedin.pk,
            },
        )
        self.assertEqual(edit_res.status_code, 302)
        self.job1.refresh_from_db()
        self.assertEqual(self.job1.company_name, "Deloitte Digital")
        self.assertEqual(self.job1.status, "Offer")

        del_res = self.client.post(reverse("job_delete", kwargs={"pk": self.job1.pk}))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(JobApplication.objects.filter(pk=self.job1.pk).exists())

    def test_folder_delete(self):
        self.client.login(username="alice", password="password123")
        f = JobFolder.objects.create(user=self.user1, name="TempFolder")
        res = self.client.post(reverse("folder_delete", kwargs={"pk": f.pk}))
        self.assertEqual(res.status_code, 302)
        self.assertFalse(JobFolder.objects.filter(pk=f.pk).exists())

    def test_folder_edit(self):
        self.client.login(username="alice", password="password123")
        f = JobFolder.objects.create(user=self.user1, name="OldName")
        res = self.client.post(
            reverse("folder_edit", kwargs={"pk": f.pk}),
            {"name": "RenamedApp"},
        )
        self.assertEqual(res.status_code, 302)
        f.refresh_from_db()
        self.assertEqual(f.name, "RenamedApp")

    def test_user_data_isolation(self):
        # Bob cannot see or edit Alice's job
        self.client.login(username="bob", password="password123")
        res = self.client.get(reverse("job_edit", kwargs={"pk": self.job1.pk}))
        self.assertEqual(res.status_code, 404)

    def test_learning_entry_create_and_search(self):
        self.client.login(username="alice", password="password123")
        res = self.client.post(
            reverse("entry_create"),
            {
                "title": "Django ORM Optimization",
                "date": "2026-10-13",
                "notes": "Learned prefetch_related and select_related",
                "code_snippet": "qs = JobFolder.objects.prefetch_related('applications')",
                "code_language": "python",
            },
        )
        self.assertEqual(res.status_code, 302)

        search_res = self.client.get(reverse("search") + "?query=Optimization")
        self.assertEqual(search_res.status_code, 200)
        self.assertContains(search_res, "Django ORM Optimization")

    def test_healthcheck_endpoint(self):
        # Test /health/ and /healthcheck/
        res = self.client.get(reverse("healthcheck"))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertIn("time_zone", data)
        self.assertIn("admin_username", data)
        self.assertIn("application_url", data)
        self.assertIn("supabase_configured", data)

        res_alt = self.client.get("/healthcheck/")
        self.assertEqual(res_alt.status_code, 200)
        self.assertEqual(res_alt.json()["status"], "healthy")

    def test_healthcheck_management_command(self):
        from io import StringIO
        from django.core.management import call_command
        out = StringIO()
        call_command("healthcheck", stdout=out)
        output = out.getvalue()
        self.assertIn("Database connection active", output)
        self.assertIn("Cache backend active", output)
        self.assertIn("Health check completed", output)

    def test_supabase_client_helpers(self):
        from tracker.supabase_client import is_supabase_configured, get_supabase_public_url
        # In test environment, if not set, returns False
        with self.settings(SUPABASE_URL="", SUPABASE_SERVICE_ROLE_KEY="", SUPABASE_STORAGE_BUCKET=""):
            self.assertFalse(is_supabase_configured())
            self.assertEqual(get_supabase_public_url("test.pdf"), "")

        with self.settings(
            SUPABASE_URL="https://xyz.supabase.co",
            SUPABASE_SERVICE_ROLE_KEY="secret-key-123",
            SUPABASE_STORAGE_BUCKET="my-bucket",
        ):
            self.assertTrue(is_supabase_configured())
            url = get_supabase_public_url("resume.pdf")
            self.assertEqual(url, "https://xyz.supabase.co/storage/v1/object/public/my-bucket/resume.pdf")

