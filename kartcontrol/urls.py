"""
URL configuration for kartcontrol project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('sessions/', include('sessions.urls', namespace='sessions')),
    path('bookings/', include('bookings.urls', namespace='bookings')),
    path('karts/', include('karts.urls', namespace='karts')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
