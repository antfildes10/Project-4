"""
Tests for karts app - Kart model and management.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Kart


class KartModelTests(TestCase):
    """Test Kart model creation, validation, and business logic."""

    def test_kart_creation(self):
        """Test that a kart can be created successfully."""
        kart = Kart.objects.create(number=1, status="ACTIVE", notes="Test kart")
        self.assertEqual(kart.number, 1)
        self.assertEqual(kart.status, "ACTIVE")
        self.assertEqual(kart.notes, "Test kart")
        self.assertIsNotNone(kart.created_at)
        self.assertIsNotNone(kart.updated_at)

    def test_kart_string_representation(self):
        """Test kart __str__ method."""
        kart = Kart.objects.create(number=5, status="ACTIVE")
        expected_str = "Kart #5 (Active)"
        self.assertEqual(str(kart), expected_str)

    def test_kart_number_unique(self):
        """Test that kart numbers must be unique."""
        Kart.objects.create(number=1, status="ACTIVE")

        # Try to create another kart with same number
        with self.assertRaises(Exception):
            Kart.objects.create(number=1, status="ACTIVE")

    def test_kart_number_min_value(self):
        """Test that kart number must be at least 1."""
        kart = Kart(number=0, status="ACTIVE")

        with self.assertRaises(ValidationError):
            kart.full_clean()

    def test_kart_number_max_value(self):
        """Test that kart number cannot exceed 99."""
        kart = Kart(number=100, status="ACTIVE")

        with self.assertRaises(ValidationError):
            kart.full_clean()

    def test_kart_number_valid_range(self):
        """Test that kart numbers in valid range (1-99) are accepted."""
        kart1 = Kart.objects.create(number=1, status="ACTIVE")
        kart99 = Kart.objects.create(number=99, status="ACTIVE")

        kart1.full_clean()  # Should not raise
        kart99.full_clean()  # Should not raise

        self.assertEqual(kart1.number, 1)
        self.assertEqual(kart99.number, 99)

    def test_kart_default_status_is_active(self):
        """Test that default status is ACTIVE."""
        kart = Kart.objects.create(number=1)
        self.assertEqual(kart.status, "ACTIVE")

    def test_kart_is_available(self):
        """Test is_available() method."""
        kart_active = Kart.objects.create(number=1, status="ACTIVE")
        kart_maintenance = Kart.objects.create(number=2, status="MAINTENANCE")

        self.assertTrue(kart_active.is_available())
        self.assertFalse(kart_maintenance.is_available())

    def test_kart_is_in_maintenance(self):
        """Test is_in_maintenance() method."""
        kart_active = Kart.objects.create(number=1, status="ACTIVE")
        kart_maintenance = Kart.objects.create(number=2, status="MAINTENANCE")

        self.assertFalse(kart_active.is_in_maintenance())
        self.assertTrue(kart_maintenance.is_in_maintenance())

    def test_kart_status_change(self):
        """Test changing kart status."""
        kart = Kart.objects.create(number=1, status="ACTIVE")
        self.assertEqual(kart.status, "ACTIVE")

        # Change to maintenance
        kart.status = "MAINTENANCE"
        kart.save()
        kart.refresh_from_db()

        self.assertEqual(kart.status, "MAINTENANCE")
        self.assertFalse(kart.is_available())
        self.assertTrue(kart.is_in_maintenance())

    def test_kart_notes_optional(self):
        """Test that notes field is optional."""
        kart = Kart.objects.create(number=1, status="ACTIVE")
        self.assertEqual(kart.notes, "")

        # Add notes
        kart.notes = "Needs tire check"
        kart.save()
        kart.refresh_from_db()
        self.assertEqual(kart.notes, "Needs tire check")

    def test_kart_ordering(self):
        """Test that karts are ordered by number."""
        Kart.objects.create(number=5)
        Kart.objects.create(number=2)
        Kart.objects.create(number=8)
        Kart.objects.create(number=1)

        karts = list(Kart.objects.all())
        self.assertEqual(karts[0].number, 1)
        self.assertEqual(karts[1].number, 2)
        self.assertEqual(karts[2].number, 5)
        self.assertEqual(karts[3].number, 8)

    def test_maintenance_kart_not_assigned_to_bookings(self):
        """Test that maintenance karts should not be assigned to bookings."""
        from bookings.models import Booking
        from sessions.models import SessionSlot, Track
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from datetime import timedelta

        User = get_user_model()

        # Create test data
        track = Track.objects.create(
            name="Test Track", address="123 Test St", phone="555-1234", email="test@track.com"
        )
        session = SessionSlot.objects.create(
            track=track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )
        user = User.objects.create_user(username="testdriver", password="testpass123")

        # Create karts
        kart_active = Kart.objects.create(number=1, status="ACTIVE")
        kart_maintenance = Kart.objects.create(number=2, status="MAINTENANCE")

        # Create booking
        booking = Booking.objects.create(session_slot=session, driver=user, status="PENDING")

        # Try to assign random kart (should only get active kart)
        result = booking.assign_random_kart()
        self.assertTrue(result)
        self.assertEqual(booking.assigned_kart, kart_active)
        self.assertNotEqual(booking.assigned_kart, kart_maintenance)

    def test_no_active_karts_available(self):
        """Test scenario when no active karts are available."""
        from bookings.models import Booking
        from sessions.models import SessionSlot, Track
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from datetime import timedelta

        User = get_user_model()

        # Create test data
        track = Track.objects.create(
            name="Test Track", address="123 Test St", phone="555-1234", email="test@track.com"
        )
        session = SessionSlot.objects.create(
            track=track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )
        user = User.objects.create_user(username="testdriver", password="testpass123")

        # All karts in maintenance
        Kart.objects.create(number=1, status="MAINTENANCE")
        Kart.objects.create(number=2, status="MAINTENANCE")

        # Create booking
        booking = Booking.objects.create(session_slot=session, driver=user, status="PENDING")

        # Try to assign random kart (should fail)
        result = booking.assign_random_kart()
        self.assertFalse(result)
        self.assertIsNone(booking.assigned_kart)
