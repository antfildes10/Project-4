"""
Booking models for managing session reservations and kart assignments.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from sessions.models import SessionSlot
from karts.models import Kart


class BookingQuerySet(models.QuerySet):
    """Custom QuerySet for Booking model with reusable filters."""

    def upcoming(self):
        """Return bookings for upcoming sessions."""
        return self.filter(
            session_slot__start_datetime__gte=timezone.now(),
            status__in=["PENDING", "CONFIRMED"],
        )

    def for_driver(self, driver):
        """Return bookings for a specific driver."""
        return self.filter(driver=driver)

    def upcoming_for_driver(self, driver):
        """Return upcoming bookings for a specific driver."""
        return self.for_driver(driver).upcoming()

    def completed(self):
        """Return completed bookings."""
        return self.filter(status="COMPLETED")

    def cancelled(self):
        """Return cancelled bookings."""
        return self.filter(status="CANCELLED")

    def pending(self):
        """Return pending bookings."""
        return self.filter(status="PENDING")

    def confirmed(self):
        """Return confirmed bookings."""
        return self.filter(status="CONFIRMED")


class BookingManager(models.Manager):
    """Custom Manager for Booking model."""

    def get_queryset(self):
        """Return custom QuerySet."""
        return BookingQuerySet(self.model, using=self._db)

    def upcoming(self):
        """Return bookings for upcoming sessions."""
        return self.get_queryset().upcoming()

    def for_driver(self, driver):
        """Return bookings for a specific driver."""
        return self.get_queryset().for_driver(driver)

    def upcoming_for_driver(self, driver):
        """Return upcoming bookings for a specific driver."""
        return self.get_queryset().upcoming_for_driver(driver)

    def completed(self):
        """Return completed bookings."""
        return self.get_queryset().completed()

    def cancelled(self):
        """Return cancelled bookings."""
        return self.get_queryset().cancelled()

    def pending(self):
        """Return pending bookings."""
        return self.get_queryset().pending()

    def confirmed(self):
        """Return confirmed bookings."""
        return self.get_queryset().confirmed()


class Booking(models.Model):
    """
    Represents a driver's booking for a specific session slot.
    Includes kart assignment and state management.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("COMPLETED", "Completed"),
    ]

    # Core relationships
    session_slot = models.ForeignKey(
        SessionSlot,
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="The session being booked",
    )
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="Driver making the booking",
    )

    # Kart assignment
    chosen_kart_number = models.PositiveIntegerField(
        null=True, blank=True, help_text="Driver preferred kart number (optional)"
    )
    assigned_kart = models.ForeignKey(
        Kart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
        help_text="Kart assigned on confirmation",
    )

    # Booking state
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="PENDING",
        help_text="Current booking status",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional notes
    driver_notes = models.TextField(blank=True, help_text="Notes from the driver")
    manager_notes = models.TextField(blank=True, help_text="Internal manager notes")

    # Custom manager
    objects = BookingManager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        indexes = [
            models.Index(fields=["driver"]),
            models.Index(fields=["session_slot"]),
            models.Index(fields=["status"]),
            # Composite indexes for common query patterns
            models.Index(fields=["driver", "session_slot"]),
            models.Index(fields=["session_slot", "status"]),
            models.Index(fields=["driver", "status"]),
        ]

    def __str__(self):
        return (
            f"{self.driver.username} - {self.session_slot} "
            f"({self.get_status_display()})"
        )

    def clean(self):
        """
        Validate booking business rules:
        1. Check capacity limits
        2. Prevent driver overlap
        3. Validate chosen kart is available
        """
        # Skip validation if being cancelled or completed
        if self.status in ["CANCELLED", "COMPLETED"]:
            return

        # Check session capacity
        if self.session_slot:
            existing_bookings = self.session_slot.bookings.filter(
                status__in=["PENDING", "CONFIRMED"]
            ).exclude(pk=self.pk)

            if existing_bookings.count() >= self.session_slot.capacity:
                raise ValidationError(
                    {"session_slot": "This session is at full capacity."}
                )

        # Check for driver overlap (same driver, overlapping time)
        if self.driver and self.session_slot:
            overlapping = Booking.objects.filter(
                driver=self.driver,
                status__in=["PENDING", "CONFIRMED"],
                session_slot__start_datetime__lt=self.session_slot.end_datetime,
                session_slot__end_datetime__gt=self.session_slot.start_datetime,
            ).exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(
                    {"session_slot": "You already have a booking during this time."}
                )

        # Validate chosen kart exists and is active
        if self.chosen_kart_number:
            try:
                kart = Kart.objects.get(number=self.chosen_kart_number)
                if not kart.is_available():
                    raise ValidationError(
                        {
                            "chosen_kart_number": (
                                f"Kart #{self.chosen_kart_number} is "
                                "currently in maintenance."
                            )
                        }
                    )
            except Kart.DoesNotExist:
                raise ValidationError(
                    {
                        "chosen_kart_number": (
                            f"Kart #{self.chosen_kart_number} does not exist."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        """Run validation before saving."""
        self.clean()
        super().save(*args, **kwargs)

    def can_be_cancelled(self):
        """Check if booking can be cancelled (before session start)."""
        return (
            self.status in ["PENDING", "CONFIRMED"]
            and self.session_slot.start_datetime > timezone.now()
        )

    def can_be_confirmed(self):
        """Check if booking can be confirmed by manager."""
        return (
            self.status == "PENDING"
            and self.session_slot.start_datetime > timezone.now()
        )

    def can_be_completed(self):
        """Check if booking can be marked complete (after session end)."""
        return (
            self.status == "CONFIRMED"
            and self.session_slot.end_datetime < timezone.now()
        )

    def assign_random_kart(self):
        """
        Assign a random available kart when confirming booking.
        Returns True if successful, False otherwise.

        Uses row-level locking to prevent race conditions.
        Checks for time-overlapping sessions to prevent double-booking.
        """
        import random
        from django.db.models import Q

        # Get all active karts with row-level lock to prevent race conditions
        available_karts = Kart.objects.filter(status="ACTIVE").select_for_update()

        # Find all sessions that overlap with this booking's session
        overlapping_sessions = SessionSlot.objects.filter(
            Q(start_datetime__lt=self.session_slot.end_datetime)
            & Q(end_datetime__gt=self.session_slot.start_datetime)
        )

        # Exclude karts assigned to ANY overlapping session (not just this one)
        assigned_kart_ids = (
            Booking.objects.filter(
                session_slot__in=overlapping_sessions,
                status__in=["CONFIRMED", "COMPLETED"],
                assigned_kart__isnull=False,
            )
            .exclude(pk=self.pk)
            .select_for_update()
            .values_list("assigned_kart_id", flat=True)
        )

        available_karts = available_karts.exclude(id__in=assigned_kart_ids)

        # If driver chose a specific kart, try to assign it
        if self.chosen_kart_number:
            try:
                chosen_kart = available_karts.get(number=self.chosen_kart_number)
                self.assigned_kart = chosen_kart
                return True
            except Kart.DoesNotExist:
                pass

        # Otherwise assign random available kart
        if available_karts.exists():
            karts_list = list(available_karts)
            self.assigned_kart = random.choice(karts_list)
            return True

        return False
