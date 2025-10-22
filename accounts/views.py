"""
Views for accounts app (authentication and user management).
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm


def register(request):
    """
    Handle user registration.
    Creates new user account and automatically logs them in.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create new user
            user = form.save()

            # Log the user in automatically
            login(request, user)

            messages.success(
                request,
                f'Welcome {user.username}! Your account has been created successfully.'
            )
            return redirect('core:home')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


@login_required
def profile(request):
    """
    Display user profile with booking history.
    Shows user details, role, and recent bookings.
    """
    from bookings.models import Booking

    # Get user's bookings ordered by creation date
    user_bookings = Booking.objects.filter(driver=request.user).order_by('-created_at')[:10]

    context = {
        'user_bookings': user_bookings,
    }
    return render(request, 'accounts/profile.html', context)
