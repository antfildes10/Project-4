"""
Tests for sessions app - SessionSlot and Track models, views, and business logic.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import timedelta

from .models import SessionSlot, Track

User = get_user_model()


class TrackModelTests(TestCase):
    """Test Track model creation and validation."""

    def test_track_creation(self):
        """Test that a track can be created successfully."""
        track = Track.objects.create(
            name="Test Track",
            address="123 Test St",
            phone="555-1234",
            email="test@track.com",
            description="Test description",
            notes="Test notes",
        )
        self.assertEqual(track.name, "Test Track")
        self.assertEqual(track.address, "123 Test St")
        self.assertIsNotNone(track.created_at)

    def test_track_string_representation(self):
        """Test track __str__ method."""
        track = Track.objects.create(name="Test Track", address="123 Test St", phone="555-1234", email="test@track.com")
        self.assertEqual(str(track), "Test Track")

    def test_only_one_track_allowed(self):
        """Test that only one track instance can exist."""
        Track.objects.create(name="Track 1", address="123 Test St", phone="555-1234", email="test@track.com")

        # Try to create second track
        with self.assertRaises(ValidationError) as context:
            Track.objects.create(name="Track 2", address="456 Test Ave", phone="555-5678", email="test2@track.com")

        self.assertIn("Only one track instance is allowed", str(context.exception))


class SessionSlotModelTests(TestCase):
    """Test SessionSlot model creation, validation, and business logic."""

    def setUp(self):
        """Set up test data."""
        self.track = Track.objects.create(
            name="Test Track", address="123 Test St", phone="555-1234", email="test@track.com", notes="Test track"
        )

    def test_session_creation(self):
        """Test that a session can be created successfully."""
        session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )
        self.assertEqual(session.track, self.track)
        self.assertEqual(session.session_type, "OPEN_SESSION")
        self.assertEqual(session.capacity, 10)
        self.assertEqual(session.price, 25.00)

    def test_session_string_representation(self):
        """Test session __str__ method."""
        session = SessionSlot.objects.create(
            track=self.track,
            session_type="GRAND_PRIX",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=35.00,
        )
        self.assertIn("Grand Prix", str(session))

    def test_session_time_validation(self):
        """Test that start time must be before end time."""
        future_time = timezone.now() + timedelta(days=1)
        past_time = timezone.now()

        session = SessionSlot(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=future_time,
            end_datetime=past_time,  # Invalid: end before start
            capacity=10,
            price=25.00,
        )

        with self.assertRaises(ValidationError) as context:
            session.save()

        self.assertIn("Start time must be before end time", str(context.exception))

    def test_session_capacity_positive(self):
        """Test that capacity must be positive."""
        from django.core.exceptions import ValidationError

        session = SessionSlot(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=0,  # Invalid: zero capacity
            price=25.00,
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_session_is_past(self):
        """Test is_past() method."""
        # Past session
        past_session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() - timedelta(days=1),
            end_datetime=timezone.now() - timedelta(hours=1),
            capacity=10,
            price=25.00,
        )
        self.assertTrue(past_session.is_past())

        # Future session
        future_session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )
        self.assertFalse(future_session.is_past())

    def test_session_is_upcoming(self):
        """Test is_upcoming() method."""
        future_session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )
        self.assertTrue(future_session.is_upcoming())

    def test_session_get_available_spots(self):
        """Test get_available_spots() method."""
        from bookings.models import Booking

        session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )

        # Initially all spots available
        self.assertEqual(session.get_available_spots(), 10)

        # Create 3 bookings
        for i in range(3):
            user = User.objects.create_user(username=f"driver{i}", password="testpass123")
            Booking.objects.create(session_slot=session, driver=user, status="PENDING")

        # Should have 7 spots left
        self.assertEqual(session.get_available_spots(), 7)

    def test_session_is_full(self):
        """Test is_full() method."""
        from bookings.models import Booking

        session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=5,
            price=25.00,
        )

        self.assertFalse(session.is_full())

        # Fill to capacity
        for i in range(5):
            user = User.objects.create_user(username=f"driver{i}", password="testpass123")
            Booking.objects.create(session_slot=session, driver=user, status="CONFIRMED")

        self.assertTrue(session.is_full())

    def test_cancelled_bookings_not_counted(self):
        """Test that cancelled bookings don't count toward capacity."""
        from bookings.models import Booking

        session = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )

        # Create 5 pending bookings
        for i in range(5):
            user = User.objects.create_user(username=f"driver{i}", password="testpass123")
            Booking.objects.create(session_slot=session, driver=user, status="PENDING")

        # Create 2 cancelled bookings
        for i in range(5, 7):
            user = User.objects.create_user(username=f"driver{i}", password="testpass123")
            Booking.objects.create(session_slot=session, driver=user, status="CANCELLED")

        # Should only count pending bookings (5 out of 10)
        self.assertEqual(session.get_available_spots(), 5)


class SessionViewTests(TestCase):
    """Test session views and public access."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create track
        self.track = Track.objects.create(
            name="Test Track", address="123 Test St", phone="555-1234", email="test@track.com", notes="Test track"
        )

        # Create users
        self.driver = User.objects.create_user(username="testdriver", password="testpass123")

        # Create sessions
        self.session1 = SessionSlot.objects.create(
            track=self.track,
            session_type="OPEN_SESSION",
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=1),
            capacity=10,
            price=25.00,
        )

        self.session2 = SessionSlot.objects.create(
            track=self.track,
            session_type="GRAND_PRIX",
            start_datetime=timezone.now() + timedelta(days=2),
            end_datetime=timezone.now() + timedelta(days=2, hours=1),
            capacity=8,
            price=35.00,
        )

    def test_session_list_public_access(self):
        """Test that session list is accessible to anonymous users."""
        response = self.client.get(reverse("sessions:session_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sessions/session_list.html")

    def test_session_list_shows_sessions(self):
        """Test that session list displays all sessions."""
        response = self.client.get(reverse("sessions:session_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("sessions", response.context)
        self.assertEqual(len(response.context["sessions"]), 2)

    def test_session_list_filter_by_type(self):
        """Test filtering sessions by type."""
        response = self.client.get(reverse("sessions:session_list") + "?session_type=GRAND_PRIX")
        self.assertEqual(response.status_code, 200)
        sessions = response.context["sessions"]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].session_type, "GRAND_PRIX")

    def test_session_list_filter_by_date(self):
        """Test filtering sessions by date."""
        date = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.get(reverse("sessions:session_list") + f"?date={date}")
        self.assertEqual(response.status_code, 200)
        sessions = response.context["sessions"]
        self.assertEqual(len(sessions), 1)

    def test_session_detail_public_access(self):
        """Test that session detail is accessible to anonymous users."""
        response = self.client.get(reverse("sessions:session_detail", args=[self.session1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "sessions/session_detail.html")

    def test_session_detail_shows_availability(self):
        """Test that session detail shows availability information."""
        response = self.client.get(reverse("sessions:session_detail", args=[self.session1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("available_spots", response.context)
        self.assertIn("is_full", response.context)
        self.assertEqual(response.context["available_spots"], 10)
        self.assertFalse(response.context["is_full"])

    def test_session_detail_authenticated_user_booking_status(self):
        """Test that authenticated users see their booking status."""
        from bookings.models import Booking

        # Create booking for user
        Booking.objects.create(session_slot=self.session1, driver=self.driver, status="PENDING")

        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("sessions:session_detail", args=[self.session1.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn("user_has_booking", response.context)
        self.assertTrue(response.context["user_has_booking"])

    def test_session_list_authenticated_shows_booking_count(self):
        """Test that authenticated users see their booking count."""
        from bookings.models import Booking

        Booking.objects.create(session_slot=self.session1, driver=self.driver, status="CONFIRMED")

        self.client.login(username="testdriver", password="testpass123")
        response = self.client.get(reverse("sessions:session_list"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("user_bookings_count", response.context)
        self.assertEqual(response.context["user_bookings_count"], 1)
        self.assertIn("user_booked_sessions", response.context)
        self.assertIn(self.session1.pk, response.context["user_booked_sessions"])
