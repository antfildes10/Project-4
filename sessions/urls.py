"""
URL patterns for sessions app (session slot management).
"""
from django.urls import path
from . import views

app_name = 'sessions'

urlpatterns = [
    # Public session listing and detail
    path('', views.session_list, name='session_list'),
    path('<int:pk>/', views.session_detail, name='session_detail'),

    # Manager-only session management
    path('create/', views.session_create, name='session_create'),
    path('<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('<int:pk>/delete/', views.session_delete, name='session_delete'),
]
