"""
URL patterns for bookings app (booking management).
"""
from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Driver booking management
    path('', views.booking_list, name='booking_list'),
    path('create/<int:session_id>/', views.booking_create, name='booking_create'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),

    # Manager actions (now handled via Django admin)
    path('<int:pk>/confirm/', views.booking_confirm, name='booking_confirm'),
    path('<int:pk>/complete/', views.booking_complete, name='booking_complete'),
]
