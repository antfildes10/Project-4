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


@login_required
def booking_create(request, session_id):
    """
    Create a new booking for a session.
    Validates capacity, driver overlap, and kart availability.
    """
    session = get_object_or_404(SessionSlot, pk=session_id)

    # Check if session is full
    if session.is_full():
        messages.error(request, 'This session is fully booked.')
        return redirect('sessions:session_detail', pk=session_id)

    # Check if session is in the past
    if session.is_past():
        messages.error(request, 'Cannot book past sessions.')
        return redirect('sessions:session_detail', pk=session_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                # Create booking but don't save yet
                booking = form.save(commit=False)
                booking.session_slot = session
                booking.driver = request.user
                booking.status = 'PENDING'

                # Validate and save (model validation will run)
                booking.save()

                messages.success(
                    request,
                    'Your booking has been created successfully. '
                    'It is pending confirmation by a manager.'
                )
                return redirect('bookings:booking_detail', pk=booking.pk)

            except ValidationError as e:
                # Display validation errors from model
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, error)
    else:
        form = BookingForm()

    context = {
        'form': form,
        'session': session,
    }
    return render(request, 'bookings/booking_form.html', context)
