from django.contrib import admin
from django.urls import path, include
from tracker.views import healthcheck_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', healthcheck_view, name='root_health'),
    path('healthcheck/', healthcheck_view, name='root_healthcheck'),
    path('', include('tracker.urls')),
]

