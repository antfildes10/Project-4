"""
Views for accounts app (authentication and user management).
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm


def register(request):
    """
    Handle user registration.
    Creates new user account and automatically logs them in.
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create new user
            user = form.save()

            # Log the user in automatically
            login(request, user)

            messages.success(request, f"Welcome {user.username}! Your account has been created successfully.")
            return redirect("core:home")
    else:
        form = UserRegistrationForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


@login_required
def profile(request):
    """
    Display user profile with booking history.
    Shows user details, role, and recent bookings.
    """
    from bookings.models import Booking

    # Get user's bookings ordered by creation date
    user_bookings = Booking.objects.filter(driver=request.user).order_by("-created_at")[:10]

    context = {
        "user_bookings": user_bookings,
    }
    return render(request, "accounts/profile.html", context)


@login_required
def profile_edit(request):
    """
    Allow users to edit their profile and account information.
    Updates both User and Profile models.
    """
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user, user=request.user)
        profile_form = ProfileEditForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:profile")
    else:
        user_form = UserEditForm(instance=request.user, user=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "accounts/profile_edit.html", context)


class CustomLoginView(LoginView):
    """
    Custom login view that redirects superusers to admin dashboard.
    Regular users are redirected to homepage.
    """

    template_name = "accounts/login.html"

    def get_success_url(self):
        """Redirect superusers to admin, regular users to homepage."""
        if self.request.user.is_superuser:
            return "/admin/"
        return "/"
