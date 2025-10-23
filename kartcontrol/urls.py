"""
URL configuration for kartcontrol project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import custom admin setup
from core.admin import setup_admin_dashboard

# Customize admin site
admin.site.site_header = "KartControl Administration"
admin.site.site_title = "KartControl Admin"
admin.site.index_title = "Operations Dashboard"

# Setup custom dashboard
setup_admin_dashboard(admin.site)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls", namespace="core")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("sessions/", include("sessions.urls", namespace="sessions")),
    path("bookings/", include("bookings.urls", namespace="bookings")),
    # Kart management now handled via Django admin
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
