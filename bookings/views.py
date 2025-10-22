"""
Views for bookings app (booking management with business logic).
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from .models import Booking
from .forms import BookingForm
from sessions.models import SessionSlot


def is_manager(user):
    """Check if user has manager role."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_manager()


@login_required
def booking_list(request):
    """
    Display list of user's bookings.
    Drivers see only their own bookings.
    """
    # Get user's bookings ordered by creation date
    bookings = Booking.objects.filter(driver=request.user).order_by('-created_at')

    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/booking_list.html', context)
