"""
Views for sessions app (session slot management).
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import SessionSlot
from .forms import SessionSlotForm


def is_manager(user):
    """Check if user has manager role."""
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_manager()


def session_list(request):
    """
    Display list of all sessions.
    Public view - accessible to all users.
    """
    # Get all upcoming sessions
    upcoming_sessions = SessionSlot.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')

    # Get past sessions for reference
    past_sessions = SessionSlot.objects.filter(
        start_datetime__lt=timezone.now()
    ).order_by('-start_datetime')[:5]

    context = {
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
    }
    return render(request, 'sessions/session_list.html', context)


def session_detail(request, pk):
    """
    Display detailed information about a specific session.
    Shows capacity, bookings, and availability.
    Public view - accessible to all users.
    """
    session = get_object_or_404(SessionSlot, pk=pk)

    # Calculate availability
    available_spots = session.get_available_spots()
    is_full = session.is_full()

    # Get confirmed bookings for this session
    confirmed_bookings = session.bookings.filter(status__in=['CONFIRMED', 'COMPLETED'])

    context = {
        'session': session,
        'available_spots': available_spots,
        'is_full': is_full,
        'confirmed_bookings': confirmed_bookings,
    }
    return render(request, 'sessions/session_detail.html', context)
