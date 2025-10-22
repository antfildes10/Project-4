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
