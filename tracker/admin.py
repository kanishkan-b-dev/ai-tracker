from django.contrib import admin
from .models import JobFolder, JobApplication, LearningEntry


@admin.register(JobFolder)
class JobFolderAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")
    search_fields = ("name", "user__username")


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("company_name", "job_title", "status", "folder", "user", "application_date")
    list_filter = ("status", "folder", "application_date")
    search_fields = ("company_name", "job_title", "user__username")


@admin.register(LearningEntry)
class LearningEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "user", "code_language", "created_at")
    list_filter = ("code_language", "date")
    search_fields = ("title", "notes", "user__username")
