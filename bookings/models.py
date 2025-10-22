"""
Booking models for managing session reservations and kart assignments.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from sessions.models import SessionSlot
from karts.models import Kart


class Booking(models.Model):
    """
    Represents a driver's booking for a specific session slot.
    Includes kart assignment and state management.
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    # Core relationships
    session_slot = models.ForeignKey(
        SessionSlot,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='The session being booked'
    )
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text='Driver making the booking'
    )

    # Kart assignment
    chosen_kart_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Driver preferred kart number (optional)'
    )
    assigned_kart = models.ForeignKey(
        Kart,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        help_text='Kart assigned on confirmation'
    )

    # Booking state
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text='Current booking status'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional notes
    driver_notes = models.TextField(
        blank=True,
        help_text='Notes from the driver'
    )
    manager_notes = models.TextField(
        blank=True,
        help_text='Internal manager notes'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        indexes = [
            models.Index(fields=['driver']),
            models.Index(fields=['session_slot']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.driver.username} - {self.session_slot} ({self.get_status_display()})"

    def clean(self):
        """
        Validate booking business rules:
        1. Check capacity limits
        2. Prevent driver overlap
        3. Validate chosen kart is available
        """
        # Skip validation if being cancelled or completed
        if self.status in ['CANCELLED', 'COMPLETED']:
            return

        # Check session capacity
        if self.session_slot:
            existing_bookings = self.session_slot.bookings.filter(
                status__in=['PENDING', 'CONFIRMED']
            ).exclude(pk=self.pk)

            if existing_bookings.count() >= self.session_slot.capacity:
                raise ValidationError({
                    'session_slot': 'This session is at full capacity.'
                })

        # Check for driver overlap (same driver, overlapping time)
        if self.driver and self.session_slot:
            overlapping = Booking.objects.filter(
                driver=self.driver,
                status__in=['PENDING', 'CONFIRMED'],
                session_slot__start_datetime__lt=self.session_slot.end_datetime,
                session_slot__end_datetime__gt=self.session_slot.start_datetime
            ).exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError({
                    'session_slot': 'You already have a booking during this time.'
                })

        # Validate chosen kart exists and is active
        if self.chosen_kart_number:
            try:
                kart = Kart.objects.get(number=self.chosen_kart_number)
                if not kart.is_available():
                    raise ValidationError({
                        'chosen_kart_number': f'Kart #{self.chosen_kart_number} is currently in maintenance.'
                    })
            except Kart.DoesNotExist:
                raise ValidationError({
                    'chosen_kart_number': f'Kart #{self.chosen_kart_number} does not exist.'
                })

    def save(self, *args, **kwargs):
        """Run validation before saving."""
        self.clean()
        super().save(*args, **kwargs)

    def can_be_cancelled(self):
        """Check if booking can be cancelled (before session start)."""
        return (
            self.status in ['PENDING', 'CONFIRMED'] and
            self.session_slot.start_datetime > timezone.now()
        )

    def can_be_confirmed(self):
        """Check if booking can be confirmed by manager."""
        return (
            self.status == 'PENDING' and
            self.session_slot.start_datetime > timezone.now()
        )

    def can_be_completed(self):
        """Check if booking can be marked complete (after session end)."""
        return (
            self.status == 'CONFIRMED' and
            self.session_slot.end_datetime < timezone.now()
        )

    def assign_random_kart(self):
        """
        Assign a random available kart when confirming booking.
        Returns True if successful, False otherwise.
        """
        # Get all active karts
        available_karts = Kart.objects.filter(status='ACTIVE')

        # Exclude karts already assigned to this session
        assigned_kart_ids = self.session_slot.bookings.filter(
            status__in=['CONFIRMED', 'COMPLETED'],
            assigned_kart__isnull=False
        ).exclude(pk=self.pk).values_list('assigned_kart_id', flat=True)

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
            self.assigned_kart = available_karts.order_by('?').first()
            return True

        return False
