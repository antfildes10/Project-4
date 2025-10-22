"""
Views for core app (public pages).
"""
from django.shortcuts import render
from django.contrib import messages
from .forms import ContactForm


def home(request):
    """
    Display the homepage with track information and recent sessions.
    """
    from sessions.models import SessionSlot
    from django.utils import timezone

    # Get upcoming sessions (next 5)
    upcoming_sessions = SessionSlot.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')[:5]

    context = {
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """
    Display the about page with track information and facility details.
    """
    from sessions.models import Track

    # Get track information (single venue)
    track = Track.objects.first()

    context = {
        'track': track,
    }
    return render(request, 'core/about.html', context)
