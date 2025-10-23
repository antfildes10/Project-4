"""
Tests for core app - Homepage, about, contact, and general views.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from sessions.models import SessionSlot, Track

User = get_user_model()


class HomeViewTests(TestCase):
    """Test homepage view and functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.track = Track.objects.create(
            name="Test Track", address="123 Test St", phone="555-1234", email="test@track.com"
        )

        # Create upcoming sessions
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

    def test_homepage_loads(self):
        """Test that homepage loads successfully."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_homepage_public_access(self):
        """Test that homepage is accessible to anonymous users."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_homepage_shows_upcoming_sessions(self):
        """Test that homepage displays upcoming sessions."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("upcoming_sessions", response.context)
        self.assertEqual(len(response.context["upcoming_sessions"]), 2)

    def test_homepage_limits_upcoming_sessions(self):
        """Test that homepage limits upcoming sessions to 6."""
        # Create 10 sessions
        for i in range(10):
            SessionSlot.objects.create(
                track=self.track,
                session_type="OPEN_SESSION",
                start_datetime=timezone.now() + timedelta(days=i + 3),
                end_datetime=timezone.now() + timedelta(days=i + 3, hours=1),
                capacity=10,
                price=25.00,
            )

        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        # Should have 6 sessions (2 from setUp + 4 more to reach limit)
        self.assertLessEqual(len(response.context["upcoming_sessions"]), 6)

    def test_homepage_authenticated_user_stats(self):
        """Test that authenticated users see their booking statistics."""
        from bookings.models import Booking

        user = User.objects.create_user(username="testuser", password="testpass123")

        # Create bookings
        Booking.objects.create(session_slot=self.session1, driver=user, status="PENDING")
        Booking.objects.create(session_slot=self.session2, driver=user, status="CONFIRMED")

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("user_bookings_count", response.context)
        self.assertIn("user_pending_count", response.context)
        self.assertIn("user_confirmed_count", response.context)
        self.assertEqual(response.context["user_bookings_count"], 2)
        self.assertEqual(response.context["user_pending_count"], 1)
        self.assertEqual(response.context["user_confirmed_count"], 1)

    def test_homepage_unauthenticated_no_stats(self):
        """Test that unauthenticated users don't see booking statistics."""
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("user_bookings_count", response.context)
        self.assertNotIn("user_pending_count", response.context)
        self.assertNotIn("user_confirmed_count", response.context)


class AboutViewTests(TestCase):
    """Test about page view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.track = Track.objects.create(
            name="Test Track",
            address="123 Test St",
            phone="555-1234",
            email="test@track.com",
            description="Test track description",
        )

    def test_about_page_loads(self):
        """Test that about page loads successfully."""
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")

    def test_about_page_public_access(self):
        """Test that about page is accessible to anonymous users."""
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)

    def test_about_page_shows_track_info(self):
        """Test that about page displays track information."""
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("track", response.context)
        self.assertEqual(response.context["track"].name, "Test Track")


class ContactViewTests(TestCase):
    """Test contact form view and submission."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_contact_page_loads(self):
        """Test that contact page loads successfully."""
        response = self.client.get(reverse("core:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/contact.html")
        self.assertIn("form", response.context)

    def test_contact_page_public_access(self):
        """Test that contact page is accessible to anonymous users."""
        response = self.client.get(reverse("core:contact"))
        self.assertEqual(response.status_code, 200)

    def test_contact_form_submission_valid(self):
        """Test successful contact form submission."""
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Test Subject",
                "message": "Test message content",
            },
        )

        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)

    def test_contact_form_submission_invalid(self):
        """Test contact form submission with invalid data."""
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "",  # Empty name
                "email": "invalid-email",  # Invalid email
                "subject": "",  # Empty subject
                "message": "",  # Empty message
            },
        )

        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_contact_form_requires_all_fields(self):
        """Test that contact form requires all fields."""
        response = self.client.post(reverse("core:contact"), {})

        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_contact_form_email_validation(self):
        """Test that contact form validates email format."""
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Test User",
                "email": "not-an-email",  # Invalid email format
                "subject": "Test Subject",
                "message": "Test message",
            },
        )

        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)


class URLRoutingTests(TestCase):
    """Test URL routing for core app."""

    def test_homepage_url_resolves(self):
        """Test that homepage URL resolves correctly."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_about_url_resolves(self):
        """Test that about URL resolves correctly."""
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)

    def test_contact_url_resolves(self):
        """Test that contact URL resolves correctly."""
        response = self.client.get(reverse("core:contact"))
        self.assertEqual(response.status_code, 200)
