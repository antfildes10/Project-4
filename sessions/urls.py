"""
URL patterns for sessions app (session slot management).
"""

from django.urls import path
from . import views

app_name = "sessions"

urlpatterns = [
    # Public session listing and detail
    path("", views.session_list, name="session_list"),
    path("<int:pk>/", views.session_detail, name="session_detail"),
    # Manager session management now handled via Django admin
]
