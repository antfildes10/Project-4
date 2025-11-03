"""
Admin configuration for karts app with CRM-style enhancements.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Kart
from bookings.models import Booking
from core.admin_utils import KART_STATUS_COLORS, create_kart_status_badge


class KartBookingInline(admin.TabularInline):
    """Inline display of bookings for a kart."""

    model = Booking
    extra = 0
    fields = ("driver", "session_slot", "status", "created_at")
    readonly_fields = ("driver", "session_slot", "created_at")
    can_delete = False
    show_change_link = True
    verbose_name = "Booking"
    verbose_name_plural = "Bookings with this Kart"
    fk_name = "assigned_kart"

    def has_add_permission(self, request, obj=None):
        """Prevent adding bookings from kart admin."""
        return False


@admin.register(Kart)
class KartAdmin(admin.ModelAdmin):
    """Admin interface for Kart model with CRM-style enhancements."""

    list_display = (
        "get_kart_number",
        "get_status_badge",
        "get_total_bookings",
        "get_upcoming_bookings",
        "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("number", "notes")
    readonly_fields = (
        "created_at",
        "updated_at",
        "get_kart_statistics",
        "get_total_bookings",
        "get_upcoming_bookings",
    )
    ordering = ("number",)
    inlines = [KartBookingInline]

    fieldsets = (
        (None, {"fields": ("get_kart_statistics",)}),
        ("Kart Details", {"fields": ("number", "status")}),
        (
            "Usage Statistics",
            {
                "fields": ("get_total_bookings", "get_upcoming_bookings"),
            },
        ),
        ("Notes", {"fields": ("notes",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_kart_number(self, obj):
        """Display kart number with icon."""
        return format_html(
            '<strong style="font-size: 1.1em;">Kart #{}</strong>', obj.number
        )

    get_kart_number.short_description = "Kart"
    get_kart_number.admin_order_field = "number"

    def get_status_badge(self, obj):
        """Display status with color badge."""
        if obj.status == "ACTIVE":
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 12px; border-radius: 3px; font-weight: bold;">Active</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: #000; padding: 4px 12px; border-radius: 3px; font-weight: bold;">Maintenance</span>'
        )

    get_status_badge.short_description = "Status"
    get_status_badge.admin_order_field = "status"

    def get_total_bookings(self, obj):
        """Display total number of bookings for this kart."""
        total = obj.bookings.count()
        completed = obj.bookings.filter(status="COMPLETED").count()
        return format_html(
            '<strong>{}</strong> total (<span style="color: #6c757d;">{} completed</span>)',
            total,
            completed,
        )

    get_total_bookings.short_description = "Total Bookings"

    def get_upcoming_bookings(self, obj):
        """Display upcoming bookings for this kart."""
        upcoming = obj.bookings.filter(
            session_slot__start_datetime__gte=timezone.now(),
            status__in=["PENDING", "CONFIRMED"],
        ).count()
        if upcoming > 0:
            return format_html(
                '<span style="color: #007bff; font-weight: bold;">{}</span>', upcoming
            )
        return format_html('<span style="color: #6c757d;">0</span>')

    get_upcoming_bookings.short_description = "Upcoming"

    def get_kart_statistics(self, obj):
        """Display comprehensive kart statistics."""
        total_bookings = obj.bookings.count()
        upcoming_bookings = obj.bookings.filter(
            session_slot__start_datetime__gte=timezone.now(),
            status__in=["PENDING", "CONFIRMED"],
        ).count()
        completed_bookings = obj.bookings.filter(status="COMPLETED").count()
        cancelled_bookings = obj.bookings.filter(status="CANCELLED").count()

        status_color = "#28a745" if obj.is_available() else "#ffc107"
        status_text = (
            "Active - Available for Assignment"
            if obj.is_available()
            else "In Maintenance - Not Available"
        )

        html = f"""
        <div style="font-family: monospace; background: #f5f5f5; padding: 15px; border-radius: 5px; border-left: 4px solid {status_color};">
            <h3 style="margin-top: 0; color: {status_color};">Kart #{obj.number} Statistics</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <p style="margin: 5px 0;"><strong>Status:</strong> <span style="color: {status_color}; font-weight: bold;">{status_text}</span></p>
                    <p style="margin: 5px 0;"><strong>Total Bookings:</strong> {total_bookings}</p>
                    <p style="margin: 5px 0;"><strong>Upcoming Bookings:</strong> <span style="color: #007bff;">{upcoming_bookings}</span></p>
                </div>
                <div>
                    <p style="margin: 5px 0;"><strong>Completed:</strong> <span style="color: #6c757d;">{completed_bookings}</span></p>
                    <p style="margin: 5px 0;"><strong>Cancelled:</strong> <span style="color: #dc3545;">{cancelled_bookings}</span></p>
                    <p style="margin: 5px 0;"><strong>Last Updated:</strong> {obj.updated_at.strftime('%d %b %Y, %H:%M')}</p>
                </div>
            </div>
        </div>
        """
        return mark_safe(html)

    get_kart_statistics.short_description = "Kart Statistics"

    actions = ["mark_active", "mark_maintenance"]

    def mark_active(self, request, queryset):
        """Bulk action to mark karts as active."""
        updated = queryset.update(status="ACTIVE")
        self.message_user(request, f"{updated} kart(s) marked as active.")

    mark_active.short_description = "Mark selected karts as Active"

    def mark_maintenance(self, request, queryset):
        """Bulk action to mark karts in maintenance."""
        updated = queryset.update(status="MAINTENANCE")
        self.message_user(request, f"{updated} kart(s) marked as maintenance.")

    mark_maintenance.short_description = "Mark selected karts as Maintenance"
