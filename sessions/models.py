"""
Session and track models for managing booking time slots.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Track(models.Model):
    """
    Represents the go-kart track facility.
    Single venue implementation - only one track record should exist.
    """

    name = models.CharField(
        max_length=200,
        help_text='Track name'
    )
    address = models.TextField(
        help_text='Full track address'
    )
    phone = models.CharField(
        max_length=20,
        help_text='Contact phone number'
    )
    email = models.EmailField(
        help_text='Contact email address'
    )
    description = models.TextField(
        blank=True,
        help_text='Track description for public display'
    )
    notes = models.TextField(
        blank=True,
        help_text='Internal notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Track'
        verbose_name_plural = 'Tracks'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Ensure only one track instance exists."""
        if not self.pk and Track.objects.exists():
            raise ValidationError('Only one track instance is allowed')
        return super().save(*args, **kwargs)


class SessionSlot(models.Model):
    """
    Represents a bookable time slot at the track.
    Drivers book into available sessions with capacity limits.
    """

    SESSION_TYPE_CHOICES = [
        ('OPEN_SESSION', 'Open Session'),
        ('GRAND_PRIX', 'Grand Prix'),
    ]

    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_type = models.CharField(
        max_length=20,
        choices=SESSION_TYPE_CHOICES,
        default='OPEN_SESSION',
        help_text='Type of racing session'
    )
    start_datetime = models.DateTimeField(
        help_text='Session start date and time'
    )
    end_datetime = models.DateTimeField(
        help_text='Session end date and time'
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text='Maximum number of drivers allowed'
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Session price in euros'
    )
    description = models.TextField(
        blank=True,
        help_text='Session description or special notes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']
        verbose_name = 'Session Slot'
        verbose_name_plural = 'Session Slots'
        indexes = [
            models.Index(fields=['track', 'start_datetime']),
            models.Index(fields=['start_datetime']),
        ]

    def __str__(self):
        return f"{self.get_session_type_display()} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """Validate that start time is before end time."""
        if self.start_datetime and self.end_datetime:
            if self.start_datetime >= self.end_datetime:
                raise ValidationError('Start time must be before end time')

    def save(self, *args, **kwargs):
        """Run validation before saving."""
        self.clean()
        return super().save(*args, **kwargs)

    def is_past(self):
        """Check if session has already occurred."""
        return self.end_datetime < timezone.now()

    def is_upcoming(self):
        """Check if session is in the future."""
        return self.start_datetime > timezone.now()

    def is_in_progress(self):
        """Check if session is currently happening."""
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime

    def get_available_spots(self):
        """Calculate remaining capacity."""
        from bookings.models import Booking
        confirmed_count = self.bookings.filter(
            status__in=['PENDING', 'CONFIRMED']
        ).count()
        return self.capacity - confirmed_count

    def is_full(self):
        """Check if session is at capacity."""
        return self.get_available_spots() <= 0
