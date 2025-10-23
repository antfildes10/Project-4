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
    Display list of all sessions with filtering.
    Public view - accessible to all users.
    """
    # Get all upcoming sessions
    sessions = SessionSlot.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')

    # Apply filters
    session_type = request.GET.get('session_type')
    date = request.GET.get('date')

    if session_type:
        sessions = sessions.filter(session_type=session_type)

    if date:
        # Filter sessions for the specific date
        sessions = sessions.filter(start_datetime__date=date)

    context = {
        'sessions': sessions,
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

    # Check if user already has a booking for this session
    user_has_booking = False
    if request.user.is_authenticated:
        user_has_booking = session.bookings.filter(
            driver=request.user,
            status__in=['PENDING', 'CONFIRMED']
        ).exists()

    context = {
        'session': session,
        'available_spots': available_spots,
        'is_full': is_full,
        'confirmed_bookings': confirmed_bookings,
        'user_has_booking': user_has_booking,
    }
    return render(request, 'sessions/session_detail.html', context)


@login_required
@user_passes_test(is_manager)
def session_create(request):
    """
    Create a new session slot.
    Manager-only view with form validation.
    """
    if request.method == 'POST':
        form = SessionSlotForm(request.POST)
        if form.is_valid():
            session = form.save()
            messages.success(
                request,
                f'Session "{session}" has been created successfully.'
            )
            return redirect('sessions:session_detail', pk=session.pk)
    else:
        form = SessionSlotForm()

    context = {
        'form': form,
        'title': 'Create New Session',
    }
    return render(request, 'sessions/session_form.html', context)


@login_required
@user_passes_test(is_manager)
def session_edit(request, pk):
    """
    Edit an existing session slot.
    Manager-only view with form validation.
    """
    session = get_object_or_404(SessionSlot, pk=pk)

    if request.method == 'POST':
        form = SessionSlotForm(request.POST, instance=session)
        if form.is_valid():
            session = form.save()
            messages.success(
                request,
                f'Session "{session}" has been updated successfully.'
            )
            return redirect('sessions:session_detail', pk=session.pk)
    else:
        form = SessionSlotForm(instance=session)

    context = {
        'form': form,
        'title': 'Edit Session',
        'session': session,
    }
    return render(request, 'sessions/session_form.html', context)


@login_required
@user_passes_test(is_manager)
def session_delete(request, pk):
    """
    Delete a session slot.
    Manager-only view with confirmation.
    """
    session = get_object_or_404(SessionSlot, pk=pk)

    if request.method == 'POST':
        session_str = str(session)
        session.delete()
        messages.success(
            request,
            f'Session "{session_str}" has been deleted successfully.'
        )
        return redirect('sessions:session_list')

    context = {
        'session': session,
    }
    return render(request, 'sessions/session_confirm_delete.html', context)
