"""
Core views for KartControl application.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Count, Q, F
from datetime import timedelta
from sessions.models import SessionSlot, Track
from bookings.models import Booking
from karts.models import Kart
from accounts.models import Profile
from .forms import ContactForm


def home(request):
    """Display homepage with upcoming sessions."""
    upcoming_sessions = SessionSlot.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')[:6]
    
    context = {
        'upcoming_sessions': upcoming_sessions,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """Display about page with track information."""
    track = Track.objects.first()
    context = {
        'track': track,
    }
    return render(request, 'core/about.html', context)


def contact(request):
    """Handle contact form submissions."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # In a real application, send email here
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('core:contact')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})


def is_manager(user):
    """Check if user is a manager."""
    return user.is_authenticated and (user.is_superuser or user.profile.is_manager())


@login_required
@user_passes_test(is_manager)
def management_dashboard(request):
    """
    Management dashboard showing session and booking statistics.
    Only accessible to managers and superusers.
    """
    now = timezone.now()
    today = now.date()
    
    # Date range filters
    tomorrow = today + timedelta(days=1)
    week_from_now = today + timedelta(days=7)
    
    # Session statistics
    total_sessions = SessionSlot.objects.count()
    upcoming_sessions = SessionSlot.objects.filter(start_datetime__gte=now).count()
    today_sessions = SessionSlot.objects.filter(
        start_datetime__date=today
    ).count()
    
    # Booking statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='PENDING').count()
    confirmed_bookings = Booking.objects.filter(status='CONFIRMED').count()
    completed_bookings = Booking.objects.filter(status='COMPLETED').count()
    
    # Today's sessions with booking counts
    todays_sessions = SessionSlot.objects.filter(
        start_datetime__date=today
    ).annotate(
        booking_count=Count('bookings')
    ).order_by('start_datetime')
    
    # Tomorrow's sessions with booking counts
    tomorrows_sessions = SessionSlot.objects.filter(
        start_datetime__date=tomorrow
    ).annotate(
        booking_count=Count('bookings')
    ).order_by('start_datetime')
    
    # This week's sessions with booking counts
    this_week_sessions = SessionSlot.objects.filter(
        start_datetime__date__gte=today,
        start_datetime__date__lte=week_from_now
    ).annotate(
        booking_count=Count('bookings')
    ).order_by('start_datetime')
    
    # Kart statistics
    total_karts = Kart.objects.count()
    active_karts = Kart.objects.filter(status='ACTIVE').count()
    maintenance_karts = Kart.objects.filter(status='MAINTENANCE').count()
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related(
        'driver', 'session_slot', 'assigned_kart'
    ).order_by('-booking_datetime')[:10]
    
    # Pending bookings requiring attention
    pending_bookings_list = Booking.objects.filter(
        status='PENDING'
    ).select_related(
        'driver', 'session_slot'
    ).order_by('session_slot__start_datetime')[:10]
    
    # Sessions needing attention (fully booked or nearly full)
    sessions_needing_attention = SessionSlot.objects.filter(
        start_datetime__gte=now
    ).annotate(
        booking_count=Count('bookings')
    ).filter(
        Q(booking_count__gte=F('capacity') - 2)  # Nearly full or full
    ).order_by('start_datetime')[:10]
    
    context = {
        # Statistics
        'total_sessions': total_sessions,
        'upcoming_sessions': upcoming_sessions,
        'today_sessions': today_sessions,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings,
        'total_karts': total_karts,
        'active_karts': active_karts,
        'maintenance_karts': maintenance_karts,
        
        # Session lists
        'todays_sessions': todays_sessions,
        'tomorrows_sessions': tomorrows_sessions,
        'this_week_sessions': this_week_sessions,
        
        # Booking lists
        'recent_bookings': recent_bookings,
        'pending_bookings_list': pending_bookings_list,
        'sessions_needing_attention': sessions_needing_attention,
        
        # Current date/time
        'now': now,
        'today': today,
    }
    
    return render(request, 'core/management_dashboard.html', context)
