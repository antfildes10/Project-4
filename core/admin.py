"""
Custom admin configuration with operational dashboard.
"""

from django.utils import timezone
from datetime import timedelta


def setup_admin_dashboard(site):
    """Configure admin site with custom dashboard."""

    # Store original index method
    original_index = site.index

    def custom_index(request, extra_context=None):
        """Custom index view with operational statistics."""
        from sessions.models import SessionSlot
        from bookings.models import Booking
        from karts.models import Kart

        today = timezone.now().date()
        now = timezone.now()
        next_week = now + timedelta(days=7)

        # Today's sessions
        todays_sessions = (
            SessionSlot.objects.filter(start_datetime__date=today)
            .select_related("track")
            .prefetch_related("bookings")
            .order_by("start_datetime")
        )

        # Pending bookings (limit to 10 most recent)
        pending_bookings = (
            Booking.objects.filter(status="PENDING")
            .select_related("driver", "session_slot")
            .order_by("-created_at")[:10]
        )

        # Upcoming sessions (next 7 days)
        upcoming_sessions = (
            SessionSlot.objects.filter(start_datetime__gte=now, start_datetime__lte=next_week)
            .select_related("track")
            .prefetch_related("bookings")
            .order_by("start_datetime")[:20]
        )

        # Kart status with upcoming booking count
        karts = Kart.objects.all().order_by("number")
        for kart in karts:
            kart.upcoming_count = kart.bookings.filter(
                session_slot__start_datetime__gte=now, status__in=["PENDING", "CONFIRMED"]
            ).count()

        # Statistics
        stats = {
            "todays_sessions": todays_sessions.count(),
            "pending_bookings": Booking.objects.filter(status="PENDING").count(),
            "confirmed_bookings": Booking.objects.filter(
                status="CONFIRMED", session_slot__start_datetime__gte=now
            ).count(),
            "active_karts": Kart.objects.filter(status="ACTIVE").count(),
            "total_karts": Kart.objects.count(),
        }

        dashboard_context = {
            "today": today,
            "todays_sessions": todays_sessions,
            "pending_bookings": pending_bookings,
            "upcoming_sessions": upcoming_sessions,
            "karts": karts,
            "stats": stats,
        }

        # Merge with extra_context
        if extra_context:
            dashboard_context.update(extra_context)

        return original_index(request, extra_context=dashboard_context)

    # Replace index method
    site.index = custom_index
