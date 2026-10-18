from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from .models import JobFolder, JobApplication, LearningEntry
from .forms import JobFolderForm, JobApplicationForm, LearningEntryForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "tracker/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    user = request.user
    
    # Job applications for user
    jobs = JobApplication.objects.filter(user=user).select_related("folder")
    total_jobs = jobs.count()
    applied_count = jobs.filter(status__iexact="Applied").count()
    interview_count = jobs.filter(Q(status__icontains="Interview") | Q(status__iexact="Interviewing")).count()
    offer_count = jobs.filter(status__iexact="Offer").count()
    rejected_count = jobs.filter(status__iexact="Rejected").count()
    
    # Folders with application counts
    folders = (
        JobFolder.objects.filter(user=user)
        .annotate(job_count=Count("applications"))
        .order_by("name")
    )
    unassigned_count = jobs.filter(folder__isnull=True).count()
    
    # Recent applications
    recent_jobs = jobs.order_by("-updated_at", "-created_at")[:10]
    
    context = {
        "user": user,
        "total_jobs": total_jobs,
        "applied_count": applied_count,
        "interview_count": interview_count,
        "offer_count": offer_count,
        "rejected_count": rejected_count,
        "folders": folders,
        "unassigned_count": unassigned_count,
        "recent_jobs": recent_jobs,
    }
    return render(request, "tracker/dashboard.html", context)


@login_required
def jobs_view(request):
    user = request.user

    # Fetch all folders belonging to user with their applications
    folders = (
        JobFolder.objects.filter(user=user)
        .prefetch_related("applications")
        .order_by("name")
    )
    
    # Applications without a folder
    unassigned_jobs = JobApplication.objects.filter(user=user, folder__isnull=True)
    total_jobs = JobApplication.objects.filter(user=user).count()

    selected_folder_id = request.GET.get("folder")
    selected_folder = None
    if selected_folder_id:
        if selected_folder_id == "unassigned":
            selected_folder = "unassigned"
        else:
            try:
                selected_folder = folders.filter(pk=int(selected_folder_id)).first()
            except (ValueError, TypeError):
                selected_folder = None

    context = {
        "user": user,
        "folders": folders,
        "unassigned_jobs": unassigned_jobs,
        "total_jobs": total_jobs,
        "selected_folder": selected_folder,
        "selected_folder_id": selected_folder_id if selected_folder else "",
    }
    return render(request, "tracker/jobs.html", context)


@login_required
def quick_add_folder_view(request):
    """
    User types an App / Folder name (e.g. LinkedIn, Indeed, etc.) and hits Okay.
    Creates that App folder and immediately opens the split screen for that folder.
    """
    if request.method == "POST":
        app_name = request.POST.get("app_name", "").strip()
        if not app_name:
            app_name = "New Folder"

        folder, created = JobFolder.objects.get_or_create(
            user=request.user, name=app_name
        )

        messages.success(
            request, f"Folder '{app_name}' created successfully!"
        )
        return redirect(f"/my-jobs/?folder={folder.pk}")

    return redirect("jobs")


@login_required
def folder_delete_view(request, pk):
    folder = get_object_or_404(JobFolder, pk=pk, user=request.user)
    if request.method == "POST":
        name = folder.name
        folder.delete()
        messages.success(request, f"Folder '{name}' deleted.")
    return redirect("jobs")


@login_required
def folder_edit_view(request, pk):
    folder = get_object_or_404(JobFolder, pk=pk, user=request.user)
    if request.method == "POST":
        new_name = request.POST.get("name", "").strip()
        if new_name:
            folder.name = new_name
            folder.save()
            messages.success(request, f"Folder renamed to '{new_name}'.")
    return redirect(f"/my-jobs/?folder={folder.pk}")


@login_required
def job_create_view(request):
    user = request.user
    selected_folder_id = request.GET.get("folder") or request.POST.get("folder")
    selected_folder = None
    if selected_folder_id:
        try:
            selected_folder = JobFolder.objects.filter(user=user, pk=int(selected_folder_id)).first()
        except (ValueError, TypeError):
            selected_folder = None

    if request.method == "POST":
        post_data = request.POST.copy()
        if not post_data.get("application_date"):
            from django.utils import timezone
            post_data["application_date"] = timezone.now().date().strftime("%Y-%m-%d")
        if post_data.get("status") == "Interviewing":
            post_data["status"] = "Interview"

        form = JobApplicationForm(user, post_data)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = user
            job.save()
            messages.success(request, f"Job at '{job.company_name}' created successfully!")
            if job.folder:
                return redirect(f"/my-jobs/?folder={job.folder.pk}")
            return redirect("my_jobs")
        else:
            errors = "; ".join([f"{f}: {', '.join(e)}" for f, e in form.errors.items()])
            messages.error(request, f"Could not create job: {errors}")
            if selected_folder:
                return redirect(f"/my-jobs/?folder={selected_folder.pk}")
            return redirect("my_jobs")
    else:
        initial_data = {}
        if selected_folder:
            initial_data["folder"] = selected_folder.pk
        form = JobApplicationForm(user, initial=initial_data)

    return render(
        request,
        "tracker/job_form.html",
        {"form": form, "title": "Add Job Application", "selected_folder": selected_folder},
    )


@login_required
def job_edit_view(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == "POST":
        post_data = request.POST.copy()
        if not post_data.get("application_date"):
            from django.utils import timezone
            post_data["application_date"] = (
                job.application_date.strftime("%Y-%m-%d") if job.application_date else timezone.now().date().strftime("%Y-%m-%d")
            )
        if post_data.get("status") == "Interviewing":
            post_data["status"] = "Interview"

        form = JobApplicationForm(request.user, post_data, instance=job)
        if form.is_valid():
            saved_job = form.save()
            messages.success(request, f"Job '{saved_job.company_name}' updated successfully.")
            if saved_job.folder:
                return redirect(f"/my-jobs/?folder={saved_job.folder.pk}")
            return redirect("my_jobs")
        else:
            errors = "; ".join([f"{f}: {', '.join(e)}" for f, e in form.errors.items()])
            messages.error(request, f"Could not update job: {errors}")
            if job.folder:
                return redirect(f"/my-jobs/?folder={job.folder.pk}")
            return redirect("my_jobs")
    else:
        form = JobApplicationForm(request.user, instance=job)

    return render(
        request,
        "tracker/job_form.html",
        {"form": form, "title": f"Edit Job: {job.company_name} - {job.job_title}", "job": job},
    )


@login_required
def job_delete_view(request, pk):
    job = get_object_or_404(JobApplication, pk=pk, user=request.user)
    folder_id = job.folder.pk if job.folder else None
    if request.method == "POST":
        company = job.company_name
        job.delete()
        messages.success(request, f"Job application for '{company}' deleted.")
    if folder_id:
        return redirect(f"/my-jobs/?folder={folder_id}")
    return redirect("jobs")



@login_required
def entry_create_view(request):
    if request.method == "POST":
        form = LearningEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, "Learning entry saved successfully!")
            return redirect("dashboard")
    else:
        form = LearningEntryForm(initial={"date": timezone.localdate()})

    return render(request, "tracker/create.html", {"form": form})


@login_required
def search_view(request):
    user = request.user
    query = request.GET.get("query", "").strip()
    entries = []
    jobs = []

    if query:
        entries = LearningEntry.objects.filter(
            Q(user=user)
            & (
                Q(title__icontains=query)
                | Q(notes__icontains=query)
                | Q(code_snippet__icontains=query)
            )
        )
        jobs = JobApplication.objects.filter(
            Q(user=user)
            & (
                Q(company_name__icontains=query)
                | Q(job_title__icontains=query)
                | Q(notes__icontains=query)
            )
        )

    return render(
        request,
        "tracker/search.html",
        {"query": query, "entries": entries, "jobs": jobs},
    )


@login_required
def entry_detail_view(request, pk):
    entry = get_object_or_404(LearningEntry, pk=pk, user=request.user)
    return render(request, "tracker/entry_detail.html", {"entry": entry})


def healthcheck_view(request):
    """
    Production health check endpoint for Render.com, uptime pingers, and system diagnostics.
    Uses:
      - DATABASE_URL (database connectivity)
      - REDIS_URL (cache connectivity)
      - HEALTHCHECK_ADMIN_USERNAME (admin user verification)
      - HEALTHCHECK_APPLICATION_URL (app domain reporting)
      - HEALTHCHECK_TIME_ZONE (active time zone reporting)
      - SUPABASE_URL & SUPABASE_STORAGE_BUCKET (Supabase storage diagnostics)
    """
    from django.http import JsonResponse
    from django.db import connection
    from django.core.cache import cache
    from django.conf import settings
    from .supabase_client import is_supabase_configured

    tz_name = getattr(settings, "HEALTHCHECK_TIME_ZONE", "UTC")
    admin_uname = getattr(settings, "HEALTHCHECK_ADMIN_USERNAME", "admin")
    app_url = getattr(settings, "HEALTHCHECK_APPLICATION_URL", "") or request.build_absolute_uri("/")

    health = {
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "time_zone": tz_name,
        "database": "unknown",
        "cache": "unknown",
        "admin_username": admin_uname,
        "admin_verified": False,
        "application_url": app_url,
        "supabase_configured": is_supabase_configured(),
        "python_version": getattr(settings, "PYTHON_VERSION", "3.14.0"),
    }

    # 1. Database Connectivity Check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            cursor.fetchone()
        health["database"] = "connected"
    except Exception as e:
        health["database"] = f"error: {str(e)}"
        health["status"] = "degraded"

    # 2. Cache / Redis Connectivity Check
    try:
        cache.set("__healthcheck__", "ok", 10)
        val = cache.get("__healthcheck__")
        health["cache"] = "connected" if val == "ok" else "disconnected"
    except Exception as e:
        health["cache"] = f"error: {str(e)}"
        if getattr(settings, "REDIS_URL", None):
            health["status"] = "degraded"

    # 3. Admin User Verification Check
    if admin_uname:
        try:
            health["admin_verified"] = User.objects.filter(username=admin_uname).exists()
        except Exception:
            health["admin_verified"] = False

    status_code = 200 if health["status"] in ("healthy", "ok") else 503
    return JsonResponse(health, status=status_code)
