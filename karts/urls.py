"""
URL patterns for karts app (kart management).
"""
from django.urls import path
from . import views

app_name = 'karts'

urlpatterns = [
    # Manager-only kart management
    path('', views.kart_list, name='kart_list'),
    path('create/', views.kart_create, name='kart_create'),
    path('<int:pk>/edit/', views.kart_edit, name='kart_edit'),
    path('<int:pk>/delete/', views.kart_delete, name='kart_delete'),
    path('<int:pk>/toggle-status/', views.kart_toggle_status, name='kart_toggle_status'),
]
