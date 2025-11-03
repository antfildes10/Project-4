"""
Shared utility functions for Django admin customization.

This module provides reusable utilities for:
- Color constants for consistent styling
- Badge generation for status/role displays
- Summary box generation for admin views
- Shared admin inline classes
"""

from django.contrib import admin
from django.utils.html import format_html

# =============================================================================
# COLOR CONSTANTS - Single source of truth for all admin colors
# =============================================================================

ROLE_COLORS = {
    'DRIVER': '#28a745',      # Green
    'MANAGER': '#dc3545',     # Red
    'MARSHAL': '#ffc107',     # Yellow/Amber
}

STATUS_COLORS = {
    'PENDING': '#ffc107',     # Yellow
    'CONFIRMED': '#28a745',   # Green
    'COMPLETED': '#6c757d',   # Gray
    'CANCELLED': '#dc3545',   # Red
    'NO_SHOW': '#6c757d',     # Gray
}

KART_STATUS_COLORS = {
    'ACTIVE': '#28a745',       # Green
    'MAINTENANCE': '#dc3545',  # Red
}

SESSION_TYPE_COLORS = {
    'OPEN': '#17a2b8',        # Info blue
    'GRAND_PRIX': '#ffc107',  # Warning yellow
}


# =============================================================================
# BADGE GENERATION UTILITIES
# =============================================================================

def create_badge(text, color, title=''):
    """
    Create a colored badge HTML element.

    Args:
        text (str): The text to display in the badge
        color (str): Hex color code for the badge background
        title (str, optional): Tooltip text for the badge

    Returns:
        SafeString: HTML-safe formatted badge element

    Example:
        >>> create_badge('Active', '#28a745', 'Kart is active')
        '<span style="..." title="Kart is active">Active</span>'
    """
    title_attr = f' title="{title}"' if title else ''
    return format_html(
        '<span style="background-color: {}; color: #ffffff; '
        'padding: 4px 10px; border-radius: 12px; font-size: 11px; '
        'font-weight: 600; text-transform: uppercase; '
        'letter-spacing: 0.5px; display: inline-block; '
        'white-space: nowrap;"{}>{}</span>',
        color,
        format_html(title_attr) if title else '',
        text
    )


def create_role_badge(role):
    """
    Create a badge for a user role.

    Args:
        role (str): The role code (e.g., 'DRIVER', 'MANAGER', 'MARSHAL')

    Returns:
        SafeString: HTML-safe formatted role badge

    Example:
        >>> create_role_badge('DRIVER')
        '<span style="...">DRIVER</span>'
    """
    color = ROLE_COLORS.get(role, '#6c757d')  # Default to gray
    return create_badge(role, color, title=f'User role: {role}')


def create_status_badge(status, status_display=None):
    """
    Create a badge for a booking status.

    Args:
        status (str): The status code (e.g., 'PENDING', 'CONFIRMED')
        status_display (str, optional): Human-readable status text

    Returns:
        SafeString: HTML-safe formatted status badge

    Example:
        >>> create_status_badge('CONFIRMED', 'Confirmed')
        '<span style="...">Confirmed</span>'
    """
    color = STATUS_COLORS.get(status, '#6c757d')  # Default to gray
    display_text = status_display or status
    return create_badge(display_text, color, title=f'Booking status: {display_text}')


def create_kart_status_badge(status, status_display=None):
    """
    Create a badge for a kart status.

    Args:
        status (str): The status code (e.g., 'ACTIVE', 'MAINTENANCE')
        status_display (str, optional): Human-readable status text

    Returns:
        SafeString: HTML-safe formatted kart status badge

    Example:
        >>> create_kart_status_badge('ACTIVE', 'Active')
        '<span style="...">Active</span>'
    """
    color = KART_STATUS_COLORS.get(status, '#6c757d')  # Default to gray
    display_text = status_display or status
    return create_badge(display_text, color, title=f'Kart status: {display_text}')


def create_session_type_badge(session_type, type_display=None):
    """
    Create a badge for a session type.

    Args:
        session_type (str): The type code (e.g., 'OPEN', 'GRAND_PRIX')
        type_display (str, optional): Human-readable type text

    Returns:
        SafeString: HTML-safe formatted session type badge

    Example:
        >>> create_session_type_badge('GRAND_PRIX', 'Grand Prix')
        '<span style="...">Grand Prix</span>'
    """
    color = SESSION_TYPE_COLORS.get(session_type, '#6c757d')  # Default to gray
    display_text = type_display or session_type
    return create_badge(display_text, color, title=f'Session type: {display_text}')


# =============================================================================
# SUMMARY BOX GENERATION UTILITIES
# =============================================================================

def create_summary_box(label, value, detail=''):
    """
    Create a summary information box for admin displays.

    Args:
        label (str): The label/title for the summary box
        value (str/int): The main value to display
        detail (str, optional): Additional detail text

    Returns:
        SafeString: HTML-safe formatted summary box

    Example:
        >>> create_summary_box('Total Bookings', 42, 'This month')
        '<div style="..."><strong>Total Bookings:</strong> 42 (This month)</div>'
    """
    detail_text = f' ({detail})' if detail else ''
    return format_html(
        '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
        'color: #ffffff; padding: 12px 16px; border-radius: 8px; '
        'margin-bottom: 10px; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);">'
        '<strong style="font-size: 12px; text-transform: uppercase; '
        'letter-spacing: 0.5px; opacity: 0.9;">{}</strong><br>'
        '<span style="font-size: 24px; font-weight: 700; '
        'text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{}</span>'
        '<span style="font-size: 13px; opacity: 0.85;">{}</span>'
        '</div>',
        label,
        value,
        detail_text
    )


def create_grid_summary_box(items):
    """
    Create a grid of summary boxes.

    Args:
        items (list): List of tuples (label, value, detail)

    Returns:
        SafeString: HTML-safe formatted grid of summary boxes

    Example:
        >>> items = [('Sessions', 5, 'today'), ('Bookings', 12, 'pending')]
        >>> create_grid_summary_box(items)
        '<div style="...">...</div>'
    """
    boxes = ''.join([
        create_summary_box(label, value, detail)
        for label, value, detail in items
    ])

    return format_html(
        '<div style="display: grid; '
        'grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); '
        'gap: 15px; margin: 20px 0;">{}</div>',
        format_html(boxes)
    )


# =============================================================================
# SHARED ADMIN INLINE CLASSES - Eliminate duplicate inline definitions
# =============================================================================

class BaseBookingInline(admin.TabularInline):
    """
    Base inline class for Booking model with shared configuration.

    This eliminates code duplication between user and session admin inlines.
    Subclass this to create context-specific inline views.
    """
    extra = 0
    can_delete = False
    show_change_link = True
    verbose_name = "Booking"
    readonly_fields = ("created_at",)

    # Must be set by subclasses
    model = None  # Will be set by Django


class UserBookingInline(BaseBookingInline):
    """Inline display of bookings on User admin page."""

    from bookings.models import Booking
    model = Booking
    fields = ("session_slot", "status", "assigned_kart", "created_at")
    readonly_fields = ("session_slot", "created_at")
    verbose_name_plural = "User Bookings"
    fk_name = "driver"


class SessionBookingInline(BaseBookingInline):
    """Inline display of bookings on SessionSlot admin page."""

    from bookings.models import Booking
    model = Booking
    fields = ("driver", "status", "assigned_kart", "created_at")
    verbose_name_plural = "Bookings for this Session"
