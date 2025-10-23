"""
Views for sessions app (session slot management).
"""

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import SessionSlot


def session_list(request):
    """
    Display list of all sessions with filtering.
    Public view - accessible to all users.
    """
    # Get all upcoming sessions
    sessions = SessionSlot.objects.filter(start_datetime__gte=timezone.now()).order_by("start_datetime")

    # Apply filters
    session_type = request.GET.get("session_type")
    date = request.GET.get("date")

    if session_type:
        sessions = sessions.filter(session_type=session_type)

    if date:
        # Filter sessions for the specific date
        sessions = sessions.filter(start_datetime__date=date)

    context = {
        "sessions": sessions,
    }

    # Add user booking information if authenticated
    if request.user.is_authenticated:
        from bookings.models import Booking

        user_bookings = Booking.objects.filter(driver=request.user, status__in=["PENDING", "CONFIRMED"])
        context["user_bookings_count"] = user_bookings.count()
        context["user_booked_sessions"] = list(user_bookings.values_list("session_slot_id", flat=True))

    return render(request, "sessions/session_list.html", context)


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
    confirmed_bookings = session.bookings.filter(status__in=["CONFIRMED", "COMPLETED"])

    # Check if user already has a booking for this session
    user_has_booking = False
    if request.user.is_authenticated:
        user_has_booking = session.bookings.filter(driver=request.user, status__in=["PENDING", "CONFIRMED"]).exists()

    context = {
        "session": session,
        "available_spots": available_spots,
        "is_full": is_full,
        "confirmed_bookings": confirmed_bookings,
        "user_has_booking": user_has_booking,
    }
    return render(request, "sessions/session_detail.html", context)
