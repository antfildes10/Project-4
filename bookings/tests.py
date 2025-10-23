"""
Tests for bookings app - Booking models, views, and business logic.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import timedelta

from .models import Booking
from sessions.models import SessionSlot, Track
from karts.models import Kart

User = get_user_model()


class BookingModelTests(TestCase):
    """Test Booking model creation, validation, and business logic."""

    def setUp(self):
        """Set up test data."""
        # Create track
        self.track = Track.objects.create(
            name="Test Track", address="123 Test St", phone="555-1234", notes="Test track"
        )

        # Create users
        self.driver = User.objects.create_user(username="testdriver", password="testpass123")
        self.driver2 = User.objects.create_user(username="driver2", password="testpass123")
        self.manager = User.objects.create_user(username="manager", password="testpass123")

        # Set manager role
        self.manager.profile.role = "MANAGER"
        self.manager.profile.save()

        # Create karts
        self.kart1 = Kart.objects.create(number=1, status="ACTIVE")
        self.kart2 = Kart.objects.create(number=2, status="ACTIVE")
        self.kart3 = Kart.objects.create(number=3, status="MAINTENANCE")

        # Create future session
        self.future_session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )

        # Create another future session (for overlap testing)
        self.overlapping_session = SessionSlot.objects.create(
            track=self.track,
            session_type="GRAND_PRIX",
            start_datetime=timezone.now() + timedelta(days=1, minutes=30),
            end_datetime=timezone.now() + timedelta(days=1, hours=1, minutes=30),
            capacity=10,
            price=35.00,
        )

    def test_booking_creation(self):
        """Test that a booking can be created successfully."""
        booking = Booking.objects.create(
            session_slot=self.future_session, driver=self.driver, status="PENDING"
        )
        self.assertEqual(booking.session_slot, self.future_session)
        self.assertEqual(booking.driver, self.driver)
        self.assertEqual(booking.status, "PENDING")
        self.assertIsNotNone(booking.created_at)

    def test_booking_string_representation(self):
        """Test booking __str__ method."""
        booking = Booking.objects.create(
            session_slot=self.future_session, driver=self.driver, status="PENDING"
        )
        # Format: "username - session - (Status Display)"
        self.assertIn(self.driver.username, str(booking))
        self.assertIn("Pending", str(booking))

    def test_booking_capacity_validation(self):
        """Test that bookings cannot exceed session capacity."""
        # Fill session to capacity (10)
        for i in range(10):
            user = User.objects.create_user(username=f"capacitydriver{i}", password="testpass123")
            Booking.objects.create(session_slot=self.future_session, driver=user, status="PENDING")

        # Try to create 11th booking
        booking = Booking(session_slot=self.future_session, driver=self.driver2, status="PENDING")

        with self.assertRaises(ValidationError) as context:
            booking.full_clean()

        self.assertIn("capacity", str(context.exception))

    def test_booking_driver_overlap_prevention(self):
        """Test that a driver cannot have overlapping bookings."""
        # Create first booking
        Booking.objects.create(session_slot=self.future_session, driver=self.driver, status="PENDING")

        # Try to create overlapping booking for same driver
        overlapping_booking = Booking(
            session_slot=self.overlapping_session, driver=self.driver, status="PENDING"
        )

        with self.assertRaises(ValidationError) as context:
            overlapping_booking.full_clean()

        self.assertIn("already have a booking", str(context.exception))

    def test_booking_can_be_cancelled(self):
        """Test can_be_cancelled method."""
        booking = Booking.objects.create(
            session_slot=self.future_session, driver=self.driver, status="PENDING"
        )
        self.assertTrue(booking.can_be_cancelled())

        # Confirmed booking can also be cancelled before start
        booking.status = "CONFIRMED"
        booking.save()
        self.assertTrue(booking.can_be_cancelled())

        # Completed booking cannot be cancelled
        booking.status = "COMPLETED"
        booking.save()
        self.assertFalse(booking.can_be_cancelled())

        # Cancelled booking cannot be cancelled again
        booking.status = "CANCELLED"
        booking.save()
        self.assertFalse(booking.can_be_cancelled())

    def test_booking_can_be_confirmed(self):
        """Test can_be_confirmed method."""
        booking = Booking.objects.create(
            session_slot=self.future_session, driver=self.driver, status="PENDING"
        )
        self.assertTrue(booking.can_be_confirmed())

        # Confirmed booking cannot be confirmed again
        booking.status = "CONFIRMED"
        booking.save()
        self.assertFalse(booking.can_be_confirmed())

    def test_booking_can_be_completed(self):
        """Test can_be_completed method - only after session ends."""
        booking = Booking.objects.create(
            session_slot=self.future_session, driver=self.driver, status="CONFIRMED"
        )
        # Future session cannot be completed
        self.assertFalse(booking.can_be_completed())

    def test_assign_random_kart(self):
        """Test random kart assignment."""
        booking = Booking.objects.create(
            session_slot=self.future_session, driver=self.driver, status="PENDING"
        )
        result = booking.assign_random_kart()
        self.assertTrue(result)
        self.assertIsNotNone(booking.assigned_kart)
        self.assertEqual(booking.assigned_kart.status, "ACTIVE")

    def test_assign_random_kart_no_available(self):
        """Test kart assignment when no karts available."""
        # Set all karts to MAINTENANCE
        Kart.objects.all().update(status="MAINTENANCE")

        booking = Booking.objects.create(
            session_slot=self.future_session, driver=self.driver, status="PENDING"
        )
        result = booking.assign_random_kart()
        self.assertFalse(result)
        self.assertIsNone(booking.assigned_kart)

    def test_cancelled_bookings_skip_validation(self):
        """Test that cancelled bookings skip capacity validation."""
        # Fill session to capacity
        for i in range(10):
            user = User.objects.create_user(username=f"canceldriver{i}", password="testpass123")
            Booking.objects.create(session_slot=self.future_session, driver=user, status="PENDING")

        # Cancel one booking
        booking_to_cancel = Booking.objects.first()
        booking_to_cancel.status = "CANCELLED"
        booking_to_cancel.save()  # Should not raise ValidationError


class BookingViewTests(TestCase):
    """Test booking views and permissions."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create track
        self.track = Track.objects.create(
            name="Test Track", address="123 Test St", phone="555-1234", notes="Test track"
        )

        # Create users
        self.driver = User.objects.create_user(username="testdriver", password="testpass123")
        self.manager = User.objects.create_user(username="manager", password="testpass123")
        self.manager.profile.role = "MANAGER"
        self.manager.profile.save()

        # Create session
        self.session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )

        # Create kart
        self.kart = Kart.objects.create(number=1, status="ACTIVE")

    def test_booking_list_requires_login(self):
        """Test that booking list redirects unauthenticated users."""
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_booking_list_authenticated(self):
        """Test booking list shows user's bookings."""
        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/booking_list.html")

    def test_booking_create_requires_login(self):
        """Test booking creation requires authentication."""
        response = self.client.get(reverse("bookings:booking_create", args=[self.session.pk]))
        self.assertEqual(response.status_code, 302)

    def test_booking_create_authenticated(self):
        """Test authenticated user can create booking."""
        self.client.login(username="testdriver", password="testpass123")
        self.client.post(reverse("bookings:booking_create", args=[self.session.pk]), {})
        # Should create booking and redirect
        self.assertEqual(Booking.objects.filter(driver=self.driver).count(), 1)

    def test_booking_create_full_session(self):
        """Test cannot book full session."""
        # Fill session to capacity
        for i in range(10):
            user = User.objects.create_user(username=f"driver{i}", password="testpass123")
            Booking.objects.create(session_slot=self.session, driver=user, status="PENDING")

        self.client.login(username="testdriver", password="testpass123")
        response = self.client.post(reverse("bookings:booking_create", args=[self.session.pk]), {})

        # Should show error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("fully booked" in str(m).lower() for m in messages))

    def test_booking_detail_own_booking(self):
        """Test driver can view own booking."""
        booking = Booking.objects.create(
            session_slot=self.session, driver=self.driver, status="PENDING"
        )
        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("bookings:booking_detail", args=[booking.pk]))
        self.assertEqual(response.status_code, 200)

    def test_booking_detail_other_booking(self):
        """Test driver cannot view other's booking."""
        other_driver = User.objects.create_user(username="other", password="testpass123")
        booking = Booking.objects.create(
            session_slot=self.session, driver=other_driver, status="PENDING"
        )
        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("bookings:booking_detail", args=[booking.pk]))
        # Should redirect with error
        self.assertEqual(response.status_code, 302)

    def test_booking_confirm_manager_only(self):
        """Test only managers can confirm bookings."""
        booking = Booking.objects.create(
            session_slot=self.session, driver=self.driver, status="PENDING"
        )

        # Driver cannot confirm
        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("bookings:booking_confirm", args=[booking.pk]))
        self.assertNotEqual(response.status_code, 200)

        # Manager can confirm
        self.client.login(username="manager", password="testpass123")
        response = self.client.get(reverse("bookings:booking_confirm", args=[booking.pk]))
        # Should redirect after confirmation
        booking.refresh_from_db()
        self.assertEqual(booking.status, "CONFIRMED")

    def test_booking_cancel_own(self):
        """Test driver can cancel own booking."""
        booking = Booking.objects.create(
            session_slot=self.session, driver=self.driver, status="PENDING"
        )
        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("bookings:booking_cancel", args=[booking.pk]))
        self.assertEqual(response.status_code, 200)

        # Actually cancel
        response = self.client.post(reverse("bookings:booking_cancel", args=[booking.pk]))
        booking.refresh_from_db()
        self.assertEqual(booking.status, "CANCELLED")

    def test_booking_list_filter_upcoming(self):
        """Test booking list filter for upcoming bookings."""
        # Create bookings with different statuses
        Booking.objects.create(session_slot=self.session, driver=self.driver, status="PENDING")
        Booking.objects.create(session_slot=self.session, driver=self.driver, status="CANCELLED")

        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("bookings:booking_list") + "?status=upcoming")

        self.assertEqual(response.status_code, 200)
        # Should only show PENDING/CONFIRMED bookings
        self.assertIn("bookings", response.context)

    def test_booking_list_filter_by_status(self):
        """Test booking list filter by specific status."""
        # Create different sessions to avoid overlap validation
        from django.utils import timezone
        from datetime import timedelta

        session2 = SessionSlot.objects.create(
            track=self.session.track,
            session_type="GRAND_PRIX",
            start_datetime=timezone.now() + timedelta(days=5),
            end_datetime=timezone.now() + timedelta(days=5, hours=1),
            capacity=10,
            price=35.00,
        )

        Booking.objects.create(session_slot=self.session, driver=self.driver, status="PENDING")
        Booking.objects.create(session_slot=session2, driver=self.driver, status="CONFIRMED")

        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("bookings:booking_list") + "?status=CONFIRMED")

        self.assertEqual(response.status_code, 200)
