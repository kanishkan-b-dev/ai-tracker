from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("", views.login_view, name="home"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard & Entries
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("create/", views.entry_create_view, name="entry_create"),
    path("search/", views.search_view, name="search"),
    path("log/<int:pk>/", views.entry_detail_view, name="entry_detail"),

    # Jobs & Folders
    path("my-jobs/", views.jobs_view, name="my_jobs"),
    path("jobs/", views.jobs_view, name="jobs"),
    path("my-jobs/quick-add/", views.quick_add_folder_view, name="quick_add_folder"),
    path("jobs/quick-add/", views.quick_add_folder_view, name="quick_add_folder_alt"),
    path("my-jobs/create/", views.job_create_view, name="job_create"),
    path("jobs/create/", views.job_create_view, name="job_create_alt"),
    path("my-jobs/edit/<int:pk>/", views.job_edit_view, name="job_edit"),
    path("jobs/edit/<int:pk>/", views.job_edit_view, name="job_edit_alt"),
    path("my-jobs/delete/<int:pk>/", views.job_delete_view, name="job_delete"),
    path("jobs/delete/<int:pk>/", views.job_delete_view, name="job_delete_alt"),
    path("my-jobs/folder-delete/<int:pk>/", views.folder_delete_view, name="folder_delete"),
    path("jobs/folder-delete/<int:pk>/", views.folder_delete_view, name="folder_delete_alt"),
    path("my-jobs/folder-edit/<int:pk>/", views.folder_edit_view, name="folder_edit"),
    # Health Check Endpoint for Render & Uptime Monitors
    path("health/", views.healthcheck_view, name="healthcheck"),
    path("healthcheck/", views.healthcheck_view, name="healthcheck_alt"),
]
