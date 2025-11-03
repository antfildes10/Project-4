"""
Custom decorators for authorization and access control.

This module provides reusable decorators to enforce role-based permissions.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def manager_required(view_func):
    """
    Decorator that requires user to have Manager role.

    Usage:
        @login_required
        @manager_required
        def my_view(request):
            # Only managers can access this view
            pass

    If the user is not authenticated, redirects to login.
    If the user is authenticated but not a manager, redirects to home with error.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect("accounts:login")

        if not (hasattr(request.user, "profile") and request.user.profile.is_manager()):
            messages.error(
                request, "You do not have permission to access this page. Manager role required."
            )
            return redirect("core:home")

        return view_func(request, *args, **kwargs)

    return wrapper


def is_manager(user):
    """
    Helper function to check if user has manager role.

    Used with @user_passes_test decorator.

    Args:
        user: Django User instance

    Returns:
        bool: True if user is authenticated and has Manager role

    Usage:
        @login_required
        @user_passes_test(is_manager)
        def my_view(request):
            pass
    """
    return (
        user.is_authenticated
        and hasattr(user, "profile")
        and user.profile.is_manager()
    )
