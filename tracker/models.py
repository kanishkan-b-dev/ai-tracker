from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class JobFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_folders")
    name = models.CharField(max_length=150, help_text="e.g. LinkedIn, Indeed, Wellfound, Direct")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["user", "name"]

    def __str__(self):
        return self.name


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ("Applied", "Applied"),
        ("Interview", "Interview"),
        ("Under Consideration", "Under Consideration"),
        ("Offer", "Offer"),
        ("Rejected", "Rejected"),
        ("Interested", "Interested"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_applications")
    folder = models.ForeignKey(
        JobFolder, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications"
    )
    company_name = models.CharField(max_length=200, help_text="Organization")
    job_title = models.CharField(max_length=200, help_text="Role")
    job_url = models.URLField(max_length=500, blank=True, help_text="Job Link")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Applied")
    application_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-application_date", "-created_at"]

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    @property
    def status_badge_class(self):
        mapping = {
            "Applied": "bg-blue-100 text-blue-800 border-blue-200",
            "Interview": "bg-yellow-100 text-yellow-800 border-yellow-200",
            "Under Consideration": "bg-purple-100 text-purple-800 border-purple-200",
            "Offer": "bg-green-100 text-green-800 border-green-200",
            "Rejected": "bg-red-100 text-red-800 border-red-200",
            "Interested": "bg-gray-100 text-gray-800 border-gray-200",
        }
        return mapping.get(self.status, "bg-gray-100 text-gray-800 border-gray-200")


class LearningEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="learning_entries")
    title = models.CharField(max_length=200)
    date = models.DateField(default=timezone.now)
    notes = models.TextField()
    code_snippet = models.TextField(blank=True)
    code_language = models.CharField(max_length=50, blank=True, default="python")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.date})"
