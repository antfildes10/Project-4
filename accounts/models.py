"""
User account models for authentication and role management.
"""

from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    Extended user profile with role-based access control.
    Linked one-to-one with Django's built-in User model.
    """

    ROLE_CHOICES = [
        ("DRIVER", "Driver"),
        ("MANAGER", "Manager"),
        ("MARSHAL", "Marshal"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default="DRIVER", help_text="User role determines access permissions"
    )
    phone_number = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def is_manager(self):
        """Check if user has manager role."""
        return self.role == "MANAGER"

    def is_marshal(self):
        """Check if user has marshal role."""
        return self.role == "MARSHAL"

    def is_driver(self):
        """Check if user has driver role."""
        return self.role == "DRIVER"
