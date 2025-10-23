"""
Kart models for managing go-kart resources.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Kart(models.Model):
    """
    Represents a single go-kart available for booking.
    Managed by track managers with status tracking.
    """

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("MAINTENANCE", "Maintenance"),
    ]

    number = models.PositiveIntegerField(
        unique=True, validators=[MinValueValidator(1), MaxValueValidator(99)], help_text="Unique kart number (1-99)"
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="ACTIVE", help_text="Current operational status of the kart"
    )
    notes = models.TextField(blank=True, help_text="Internal notes about kart condition or maintenance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["number"]
        verbose_name = "Kart"
        verbose_name_plural = "Karts"

    def __str__(self):
        return f"Kart #{self.number} ({self.get_status_display()})"

    def is_available(self):
        """Check if kart is available for booking (ACTIVE status)."""
        return self.status == "ACTIVE"

    def is_in_maintenance(self):
        """Check if kart is currently in maintenance."""
        return self.status == "MAINTENANCE"
