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
from core.decorators import is_manager


@login_required
def booking_list(request):
    """
    Display list of user's bookings with filtering.
    Drivers see only their own bookings.
    """
    from django.utils import timezone

    # Get user's bookings
    bookings = Booking.objects.filter(driver=request.user).select_related(
        "session_slot", "assigned_kart"
    )

    # Apply status filter
    status_filter = request.GET.get("status", "all")

    if status_filter == "upcoming":
        # Show confirmed bookings for future sessions
        bookings = bookings.filter(
            status__in=["PENDING", "CONFIRMED"],
            session_slot__start_datetime__gte=timezone.now(),
        )
    elif status_filter in ["PENDING", "CONFIRMED", "COMPLETED", "CANCELLED"]:
        # Filter by specific status
        bookings = bookings.filter(status=status_filter)
    # else: show all bookings

    # Order by session date (most recent first)
    bookings = bookings.order_by("-session_slot__start_datetime")

    context = {
        "bookings": bookings,
    }
    return render(request, "bookings/booking_list.html", context)


@login_required
def booking_create(request, session_id):
    """
    Create a new booking for a session.
    Validates capacity, driver overlap, and kart availability.
    """
    session = get_object_or_404(SessionSlot, pk=session_id)

    # Check if session is full
    if session.is_full():
        messages.error(request, "This session is fully booked.")
        return redirect("sessions:session_detail", pk=session_id)

    # Check if session is in the past
    if session.is_past():
        messages.error(request, "Cannot book past sessions.")
        return redirect("sessions:session_detail", pk=session_id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        # Set required fields on the form instance before validation
        form.instance.session_slot = session
        form.instance.driver = request.user
        form.instance.status = "PENDING"

        if form.is_valid():
            try:
                # Save the booking (model validation already ran during is_valid)
                booking = form.save()

                messages.success(
                    request,
                    "Your booking has been created successfully. "
                    "It is pending confirmation by a manager.",
                )
                return redirect("bookings:booking_detail", pk=booking.pk)

            except ValidationError as e:
                # Display validation errors from model
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, error)
    else:
        form = BookingForm()

    context = {
        "form": form,
        "session": session,
    }
    return render(request, "bookings/booking_form.html", context)


@login_required
def booking_detail(request, pk):
    """
    Display booking details.
    Drivers can only view their own bookings.
    Managers can view all bookings.
    """
    booking = get_object_or_404(Booking, pk=pk)

    # Check permissions: driver can only view own bookings
    if not is_manager(request.user) and booking.driver != request.user:
        messages.error(request, "You do not have permission to view this booking.")
        return redirect("bookings:booking_list")

    context = {
        "booking": booking,
    }
    return render(request, "bookings/booking_detail.html", context)


@login_required
def booking_cancel(request, pk):
    """
    Cancel a booking.
    Drivers can cancel their own bookings before session starts.
    Managers can cancel any booking before session starts.
    """
    booking = get_object_or_404(Booking, pk=pk)

    # Check permissions: driver can only cancel own bookings
    if not is_manager(request.user) and booking.driver != request.user:
        messages.error(request, "You do not have permission to cancel this booking.")
        return redirect("bookings:booking_list")

    # Check if booking can be cancelled
    if not booking.can_be_cancelled():
        messages.error(
            request,
            "This booking cannot be cancelled. It may have already "
            "started or been completed.",
        )
        return redirect("bookings:booking_detail", pk=booking.pk)

    if request.method == "POST":
        booking.status = "CANCELLED"
        booking.save()

        messages.success(request, "Your booking has been cancelled successfully.")
        return redirect("bookings:booking_list")

    context = {
        "booking": booking,
    }
    return render(request, "bookings/booking_confirm_delete.html", context)


@login_required
@user_passes_test(is_manager)
def booking_confirm(request, pk):
    """
    Confirm a pending booking and assign kart.
    Manager-only action.
    """
    booking = get_object_or_404(Booking, pk=pk)

    # Check if booking can be confirmed
    if not booking.can_be_confirmed():
        messages.error(
            request,
            "This booking cannot be confirmed. It may have already "
            "started or is not pending.",
        )
        return redirect("bookings:booking_detail", pk=booking.pk)

    # Try to assign a kart (wrapped in transaction for data consistency)
    from django.db import transaction

    try:
        with transaction.atomic():
            if booking.assign_random_kart():
                booking.status = "CONFIRMED"
                booking.save()

                messages.success(
                    request,
                    f"Booking confirmed for {booking.driver.username}. "
                    f"Kart #{booking.assigned_kart.number} has been assigned.",
                )
            else:
                messages.error(
                    request,
                    "No available karts for this session. Please check kart "
                    "status or session conflicts.",
                )
    except Exception as e:
        messages.error(
            request,
            f"Error confirming booking: {str(e)}",
        )

    return redirect("bookings:booking_detail", pk=booking.pk)


@login_required
@user_passes_test(is_manager)
def booking_complete(request, pk):
    """
    Mark a booking as completed after session ends.
    Manager-only action.
    """
    booking = get_object_or_404(Booking, pk=pk)

    # Check if booking can be completed
    if not booking.can_be_completed():
        messages.error(
            request,
            "This booking cannot be completed. The session may not have ended yet.",
        )
        return redirect("bookings:booking_detail", pk=booking.pk)

    booking.status = "COMPLETED"
    booking.save()

    messages.success(
        request, f"Booking for {booking.driver.username} has been marked as completed."
    )
    return redirect("bookings:booking_detail", pk=booking.pk)
