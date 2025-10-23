"""
Tests for accounts app - Profile model, registration, and user management.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Profile

User = get_user_model()


class ProfileModelTests(TestCase):
    """Test Profile model creation and business logic."""

    def test_profile_creation_on_user_signup(self):
        """Test that profile is automatically created when user is created."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)

    def test_profile_default_role_is_driver(self):
        """Test that default role is DRIVER."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertEqual(user.profile.role, "DRIVER")

    def test_profile_string_representation(self):
        """Test profile __str__ method."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        expected_str = "testuser - Driver"
        self.assertEqual(str(user.profile), expected_str)

    def test_profile_is_manager(self):
        """Test is_manager() method."""
        user = User.objects.create_user(username="manager", password="testpass123")
        user.profile.role = "MANAGER"
        user.profile.save()
        self.assertTrue(user.profile.is_manager())
        self.assertFalse(user.profile.is_driver())
        self.assertFalse(user.profile.is_marshal())

    def test_profile_is_marshal(self):
        """Test is_marshal() method."""
        user = User.objects.create_user(username="marshal", password="testpass123")
        user.profile.role = "MARSHAL"
        user.profile.save()
        self.assertTrue(user.profile.is_marshal())
        self.assertFalse(user.profile.is_driver())
        self.assertFalse(user.profile.is_manager())

    def test_profile_is_driver(self):
        """Test is_driver() method."""
        user = User.objects.create_user(username="driver", password="testpass123")
        self.assertTrue(user.profile.is_driver())
        self.assertFalse(user.profile.is_manager())
        self.assertFalse(user.profile.is_marshal())

    def test_profile_phone_number_optional(self):
        """Test that phone number is optional."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertEqual(user.profile.phone_number, "")

        # Set phone number
        user.profile.phone_number = "555-1234"
        user.profile.save()
        self.assertEqual(user.profile.phone_number, "555-1234")

    def test_profile_timestamps(self):
        """Test that created_at and updated_at are set."""
        user = User.objects.create_user(username="testuser", password="testpass123")
        self.assertIsNotNone(user.profile.created_at)
        self.assertIsNotNone(user.profile.updated_at)


class RegistrationViewTests(TestCase):
    """Test user registration views and forms."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_registration_page_loads(self):
        """Test that registration page loads successfully."""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")
        self.assertIn("form", response.context)

    def test_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@test.com",
                "password1": "testpass123!",
                "password2": "testpass123!",
            },
        )

        # Should redirect to home page
        self.assertEqual(response.status_code, 302)

        # User should be created
        self.assertTrue(User.objects.filter(username="newuser").exists())

        # Profile should be created automatically
        user = User.objects.get(username="newuser")
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.role, "DRIVER")

    def test_registration_auto_login(self):
        """Test that user is automatically logged in after registration."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@test.com",
                "password1": "testpass123!",
                "password2": "testpass123!",
            },
            follow=True,
        )

        # User should be authenticated
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].username, "newuser")

    def test_registration_password_mismatch(self):
        """Test registration fails with mismatched passwords."""
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "newuser@test.com",
                "password1": "testpass123!",
                "password2": "differentpass!",
            },
        )

        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)

        # User should not be created
        self.assertFalse(User.objects.filter(username="newuser").exists())

    def test_registration_duplicate_username(self):
        """Test registration fails with duplicate username."""
        # Create existing user
        User.objects.create_user(username="existinguser", password="testpass123")

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "existinguser",
                "email": "new@test.com",
                "password1": "testpass123!",
                "password2": "testpass123!",
            },
        )

        # Should not redirect (form has errors)
        self.assertEqual(response.status_code, 200)

        # Should only have one user with this username
        self.assertEqual(User.objects.filter(username="existinguser").count(), 1)


class ProfileViewTests(TestCase):
    """Test profile viewing and editing views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_profile_view_requires_login(self):
        """Test that profile view redirects unauthenticated users."""
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_profile_view_authenticated(self):
        """Test profile view loads for authenticated user."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_view_shows_bookings(self):
        """Test profile view shows user's recent bookings."""
        from bookings.models import Booking
        from sessions.models import SessionSlot, Track
        from django.utils import timezone
        from datetime import timedelta

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
        Booking.objects.create(session_slot=session, driver=self.user, status="PENDING")

        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("user_bookings", response.context)
        self.assertEqual(len(response.context["user_bookings"]), 1)

    def test_profile_edit_requires_login(self):
        """Test that profile edit redirects unauthenticated users."""
        response = self.client.get(reverse("accounts:profile_edit"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_profile_edit_loads(self):
        """Test profile edit page loads for authenticated user."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("accounts:profile_edit"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile_edit.html")
        self.assertIn("user_form", response.context)
        self.assertIn("profile_form", response.context)

    def test_profile_edit_success(self):
        """Test successful profile update."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("accounts:profile_edit"),
            {
                "username": "testuser",
                "email": "updated@test.com",
                "first_name": "Test",
                "last_name": "User",
                "phone_number": "555-1234",
            },
        )

        # Should redirect to profile page
        self.assertEqual(response.status_code, 302)

        # Profile should be updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updated@test.com")
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.profile.phone_number, "555-1234")


class AuthenticationFlowTests(TestCase):
    """Test authentication flow (login, logout)."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(reverse("accounts:login"), {"username": "testuser", "password": "testpass123"})

        # Should redirect
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        response = self.client.post(reverse("accounts:login"), {"username": "testuser", "password": "wrongpassword"})

        # Should not redirect (show error)
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """Test logout clears session."""
        self.client.login(username="testuser", password="testpass123")

        # User should be logged in
        response = self.client.get(reverse("core:home"))
        self.assertTrue(response.context["user"].is_authenticated)

        # Logout
        self.client.get(reverse("accounts:logout"))

        # User should be logged out
        response = self.client.get(reverse("core:home"))
        self.assertFalse(response.context["user"].is_authenticated)
