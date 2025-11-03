"""
Admin configuration for sessions app with CRM-style enhancements.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Track, SessionSlot
from bookings.models import Booking
from core.admin_utils import SESSION_TYPE_COLORS, create_session_type_badge


class BookingInline(admin.TabularInline):
    """Inline display of bookings for a session."""

    model = Booking
    extra = 0
    fields = ("driver", "status", "assigned_kart", "created_at")
    readonly_fields = ("created_at",)
    can_delete = False
    show_change_link = True
    verbose_name = "Booking"
    verbose_name_plural = "Bookings for this Session"


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Track model."""

    list_display = ("name", "phone", "email", "get_session_count", "created_at")
    search_fields = ("name", "address", "phone", "email")
    readonly_fields = (
        "created_at",
        "updated_at",
        "get_session_count",
        "get_track_stats",
    )

    fieldsets = (
        ("Track Information", {"fields": ("name", "address", "phone", "email")}),
        (
            "Statistics",
            {
                "fields": ("get_session_count", "get_track_stats"),
            },
        ),
        ("Description", {"fields": ("description",)}),
        ("Internal Notes", {"fields": ("notes",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_session_count(self, obj):
        """Display total number of sessions for this track."""
        total = obj.sessions.count()
        upcoming = obj.sessions.filter(start_datetime__gte=timezone.now()).count()
        return format_html(
            '<strong>{}</strong> total (<span style="color: #28a745;">{} upcoming</span>)',
            total,
            upcoming,
        )

    get_session_count.short_description = "Sessions"

    def get_track_stats(self, obj):
        """Display comprehensive track statistics."""
        from django.utils import timezone
        from bookings.models import Booking

        total_sessions = obj.sessions.count()
        upcoming_sessions = obj.sessions.filter(
            start_datetime__gte=timezone.now()
        ).count()
        past_sessions = obj.sessions.filter(end_datetime__lt=timezone.now()).count()

        total_bookings = Booking.objects.filter(session_slot__track=obj).count()
        confirmed_bookings = Booking.objects.filter(
            session_slot__track=obj, status="CONFIRMED"
        ).count()

        html = f"""
        <div style="font-family: monospace; background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff;">
            <h3 style="margin-top: 0; color: #007bff;">Track Statistics</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <p style="margin: 5px 0;"><strong>Total Sessions:</strong> {total_sessions}</p>
                    <p style="margin: 5px 0;"><strong>Upcoming Sessions:</strong> <span style="color: #28a745;">{upcoming_sessions}</span></p>
                    <p style="margin: 5px 0;"><strong>Past Sessions:</strong> <span style="color: #6c757d;">{past_sessions}</span></p>
                </div>
                <div>
                    <p style="margin: 5px 0;"><strong>Total Bookings:</strong> {total_bookings}</p>
                    <p style="margin: 5px 0;"><strong>Confirmed Bookings:</strong> <span style="color: #28a745;">{confirmed_bookings}</span></p>
                </div>
            </div>
        </div>
        """
        return mark_safe(html)

    get_track_stats.short_description = "Statistics"


@admin.register(SessionSlot)
class SessionSlotAdmin(admin.ModelAdmin):
    """Admin interface for SessionSlot model."""

    list_display = (
        "get_session_name",
        "get_session_type_badge",
        "start_datetime",
        "end_datetime",
        "get_capacity_display",
        "get_booked_count",
        "get_available_spots",
        "price",
    )
    list_filter = ("session_type", "start_datetime", "track")
    search_fields = ("description",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "get_booked_count",
        "get_available_spots",
        "get_session_summary",
    )
    date_hierarchy = "start_datetime"
    ordering = ("-start_datetime",)
    inlines = [BookingInline]

    fieldsets = (
        (None, {"fields": ("get_session_summary",)}),
        (
            "Session Details",
            {"fields": ("track", "session_type", "start_datetime", "end_datetime")},
        ),
        (
            "Capacity & Pricing",
            {
                "fields": (
                    "capacity",
                    "price",
                    "get_booked_count",
                    "get_available_spots",
                )
            },
        ),
        ("Description", {"fields": ("description",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_session_name(self, obj):
        """Display session type and date."""
        return str(obj)

    get_session_name.short_description = "Session"

    def get_booked_count(self, obj):
        """Display count of confirmed/pending bookings."""
        count = obj.bookings.filter(status__in=["PENDING", "CONFIRMED"]).count()
        if count >= obj.capacity:
            return f"{count} (FULL)"
        return count

    get_booked_count.short_description = "Booked"

    def get_available_spots(self, obj):
        """Display available spots."""
        available = obj.get_available_spots()
        if available <= 0:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">0 (FULL)</span>'
            )
        elif available <= 3:
            return format_html(
                '<span style="color: #ffc107; font-weight: bold;">{}</span>', available
            )
        return format_html('<span style="color: #28a745;">{}</span>', available)

    get_available_spots.short_description = "Available"

    def get_session_type_badge(self, obj):
        """Display session type with color badge."""
        if obj.session_type == "GRAND_PRIX":
            return format_html(
                '<span style="background-color: #ffc107; color: #000; padding: 3px 10px; border-radius: 3px; font-weight: bold;">Grand Prix</span>'
            )
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; border-radius: 3px;">Open Session</span>'
        )

    get_session_type_badge.short_description = "Type"
    get_session_type_badge.admin_order_field = "session_type"

    def get_capacity_display(self, obj):
        """Display capacity with visual indicator."""
        booked = obj.bookings.filter(status__in=["PENDING", "CONFIRMED"]).count()
        percentage = (booked / obj.capacity * 100) if obj.capacity > 0 else 0

        if percentage >= 90:
            color = "#dc3545"  # Red
        elif percentage >= 70:
            color = "#ffc107"  # Yellow
        else:
            color = "#28a745"  # Green

        return format_html(
            '{} <span style="color: {};">({}%)</span>',
            int(obj.capacity),
            color,
            int(round(percentage)),
        )

    get_capacity_display.short_description = "Capacity"

    def get_session_summary(self, obj):
        """Display comprehensive session summary."""
        booked_count = obj.bookings.filter(status__in=["PENDING", "CONFIRMED"]).count()
        available = obj.get_available_spots()
        percentage = (booked_count / obj.capacity * 100) if obj.capacity > 0 else 0

        status_color = "#28a745" if available > 0 else "#dc3545"
        status_text = "Available" if available > 0 else "FULL"

        html = f"""
        <div style="font-family: monospace; background: #f5f5f5; padding: 15px; border-radius: 5px;">
            <h3 style="margin-top: 0;">Session Summary</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <p><strong>Type:</strong> {obj.get_session_type_display()}</p>
                    <p><strong>Track:</strong> {obj.track.name}</p>
                    <p><strong>Date:</strong> {obj.start_datetime.strftime('%A, %d %B %Y')}</p>
                    <p><strong>Time:</strong> {obj.start_datetime.strftime('%H:%M')} - {obj.end_datetime.strftime('%H:%M')}</p>
                </div>
                <div>
                    <p><strong>Price:</strong> €{obj.price}</p>
                    <p><strong>Capacity:</strong> {obj.capacity} drivers</p>
                    <p><strong>Booked:</strong> {booked_count} drivers ({percentage:.0f}%)</p>
                    <p><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{status_text}</span></p>
                </div>
            </div>
        </div>
        """
        return mark_safe(html)

    get_session_summary.short_description = "Session Summary"
