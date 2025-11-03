"""
Core views for KartControl application.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from sessions.models import SessionSlot, Track
from .forms import ContactForm


def home(request):
    """Display homepage with upcoming sessions."""
    upcoming_sessions = SessionSlot.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by("start_datetime")[:6]

    context = {
        "upcoming_sessions": upcoming_sessions,
    }

    # Add user booking statistics if authenticated
    if request.user.is_authenticated:
        from bookings.models import Booking

        user_bookings = Booking.objects.filter(driver=request.user)
        context["user_bookings_count"] = user_bookings.count()
        context["user_pending_count"] = user_bookings.filter(status="PENDING").count()
        context["user_confirmed_count"] = user_bookings.filter(
            status="CONFIRMED"
        ).count()

    return render(request, "core/home.html", context)


def about(request):
    """Display about page with track information."""
    track = Track.objects.first()
    context = {
        "track": track,
    }
    return render(request, "core/about.html", context)


def contact(request):
    """Handle contact form submissions."""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # In a real application, send email here
            messages.success(
                request, "Thank you for your message! We will get back to you soon."
            )
            return redirect("core:contact")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"form": form})


def privacy_policy(request):
    """Display privacy policy page."""
    return render(request, "core/privacy.html")


def terms_of_service(request):
    """Display terms of service page."""
    return render(request, "core/terms.html")
