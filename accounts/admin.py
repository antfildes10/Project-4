"""
Admin configuration for accounts app with CRM-style enhancements.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Profile
from bookings.models import Booking
from core.admin_utils import ROLE_COLORS, create_role_badge


class BookingInline(admin.TabularInline):
    """Inline display of bookings for a user."""

    model = Booking
    extra = 0
    fields = ("session_slot", "status", "assigned_kart", "created_at")
    readonly_fields = ("session_slot", "created_at")
    can_delete = False
    show_change_link = True
    verbose_name = "Booking"
    verbose_name_plural = "User Bookings"
    fk_name = "driver"


class ProfileInline(admin.StackedInline):
    """Inline admin for Profile model within User admin."""

    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ("role", "role_permissions_summary", "phone_number")
    readonly_fields = ("role_permissions_summary",)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """Add helpful descriptions to role choices."""
        if db_field.name == "role":
            kwargs["help_text"] = mark_safe(
                """
                <div style="margin-top: 10px; padding: 10px; background: #f0f8ff; border-left: 4px solid #007bff; border-radius: 4px;">
                    <strong style="color: #007bff;">Role Descriptions:</strong><br><br>
                    <strong style="color: #17a2b8;">🏎️ Driver:</strong> Regular users who can view sessions and manage their own bookings.<br>
                    <strong style="color: #ffc107;">👔 Manager:</strong> Staff members who can manage all bookings, sessions, karts, and access admin dashboard.<br>
                    <strong style="color: #6f42c1;">🛡️ Marshal:</strong> Safety officers who can view all bookings and monitor track operations.
                </div>
                """
            )
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def role_permissions_summary(self, obj):
        """Display detailed permissions for the selected role."""
        if not obj or not obj.pk:
            return mark_safe(
                '<p style="color: #999;">Save user first to see role permissions.</p>'
            )

        permissions_map = {
            "DRIVER": {
                "icon": "🏎️",
                "color": "#17a2b8",
                "can_do": [
                    "View available racing sessions",
                    "Create their own bookings",
                    "View their own bookings",
                    "Cancel their own bookings (before session starts)",
                ],
                "cannot_do": [
                    "View other users' bookings",
                    "Manage sessions or karts",
                    "Access admin dashboard",
                ],
            },
            "MANAGER": {
                "icon": "👔",
                "color": "#ffc107",
                "can_do": [
                    "All Driver permissions",
                    "View all bookings from all users",
                    "Create/edit/delete any booking",
                    "Manage sessions and karts",
                    "Access full admin dashboard",
                ],
                "cannot_do": [
                    "None - Managers have full access",
                ],
            },
            "MARSHAL": {
                "icon": "🛡️",
                "color": "#6f42c1",
                "can_do": [
                    "View all racing sessions",
                    "View all bookings from all users",
                    "Cancel unsafe bookings (safety override)",
                    "Monitor track operations",
                ],
                "cannot_do": [
                    "Create or edit sessions",
                    "Manage kart fleet",
                    "Access full admin features",
                ],
            },
        }

        role_info = permissions_map.get(obj.role, None)
        if not role_info:
            return ""

        html = f"""
        <div style="margin-top: 10px; padding: 15px; background: #f8f9fa; border-left: 4px solid {role_info['color']}; border-radius: 4px;">
            <h4 style="margin-top: 0; color: {role_info['color']};">
                {role_info['icon']} {obj.get_role_display()} Permissions
            </h4>

            <div style="margin-bottom: 15px;">
                <strong style="color: #28a745;">✅ Can Do:</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    {''.join(f'<li>{item}</li>' for item in role_info['can_do'])}
                </ul>
            </div>

            <div>
                <strong style="color: #dc3545;">❌ Cannot Do:</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    {''.join(f'<li style="color: #6c757d;">{item}</li>' for item in role_info['cannot_do'])}
                </ul>
            </div>
        </div>
        """
        return mark_safe(html)

    role_permissions_summary.short_description = "What This Role Can Do"


class UserAdmin(BaseUserAdmin):
    """Extended User admin with Profile inline and CRM features."""

    inlines = (ProfileInline, BookingInline)
    list_display = (
        "username",
        "get_full_name_display",
        "email",
        "get_role_badge",
        "get_booking_count",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "profile__role",
        "date_joined",
    )
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "profile__phone_number",
    )

    # Hide Groups and Permissions - we use Profile.role instead
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email"),
            },
        ),
    )

    def get_full_name_display(self, obj):
        """Display user's full name."""
        full_name = obj.get_full_name()
        if full_name:
            return full_name
        return format_html('<span style="color: #999;">No name set</span>')

    get_full_name_display.short_description = "Full Name"

    def get_role_badge(self, obj):
        """Display user role with color badge."""
        if not hasattr(obj, "profile"):
            return format_html('<span style="color: #999;">No profile</span>')

        return create_role_badge(obj.profile.role)

    get_role_badge.short_description = "Role"
    get_role_badge.admin_order_field = "profile__role"

    def get_booking_count(self, obj):
        """Display user's booking count."""
        total = obj.bookings.count()
        upcoming = obj.bookings.filter(
            session_slot__start_datetime__gte=timezone.now(),
            status__in=["PENDING", "CONFIRMED"],
        ).count()

        if total == 0:
            return format_html('<span style="color: #6c757d;">0</span>')

        return format_html(
            '<strong>{}</strong> (<span style="color: #007bff;">{} upcoming</span>)',
            total,
            upcoming,
        )

    get_booking_count.short_description = "Bookings"


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Unregister Groups - we don't use Django's permission system
admin.site.unregister(Group)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model with CRM enhancements."""

    list_display = (
        "get_user_link",
        "get_role_badge",
        "phone_number",
        "get_booking_count",
        "created_at",
    )
    list_filter = ("role", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "phone_number",
        "user__first_name",
        "user__last_name",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "get_profile_summary",
        "get_booking_count",
    )

    fieldsets = (
        (None, {"fields": ("get_profile_summary",)}),
        ("User Information", {"fields": ("user",)}),
        ("Profile Details", {"fields": ("role", "phone_number")}),
        ("Statistics", {"fields": ("get_booking_count",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_user_link(self, obj):
        """Display clickable link to user."""
        from django.urls import reverse

        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    get_user_link.short_description = "User"
    get_user_link.admin_order_field = "user__username"

    def get_role_badge(self, obj):
        """Display role with color badge."""
        return create_role_badge(obj.role)

    get_role_badge.short_description = "Role"
    get_role_badge.admin_order_field = "role"

    def get_booking_count(self, obj):
        """Display booking statistics."""
        total = obj.user.bookings.count()
        upcoming = obj.user.bookings.filter(
            session_slot__start_datetime__gte=timezone.now(),
            status__in=["PENDING", "CONFIRMED"],
        ).count()
        completed = obj.user.bookings.filter(status="COMPLETED").count()

        return format_html(
            '<strong>{}</strong> total (<span style="color: #007bff;">{} upcoming</span>, <span style="color: #6c757d;">{} completed</span>)',
            total,
            upcoming,
            completed,
        )

    get_booking_count.short_description = "Bookings"

    def get_profile_summary(self, obj):
        """Display comprehensive profile summary."""
        total_bookings = obj.user.bookings.count()
        upcoming_bookings = obj.user.bookings.filter(
            session_slot__start_datetime__gte=timezone.now(),
            status__in=["PENDING", "CONFIRMED"],
        ).count()
        completed_bookings = obj.user.bookings.filter(status="COMPLETED").count()
        cancelled_bookings = obj.user.bookings.filter(status="CANCELLED").count()

        role_color = ROLE_COLORS.get(obj.role, "#6c757d")

        html = f"""
        <div style="font-family: monospace; background: #f5f5f5; padding: 15px; border-radius: 5px; border-left: 4px solid {role_color};">
            <h3 style="margin-top: 0; color: {role_color};">{obj.user.username}'s Profile</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div>
                    <p style="margin: 5px 0;"><strong>Full Name:</strong> {obj.user.get_full_name() or 'Not set'}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {obj.user.email}</p>
                    <p style="margin: 5px 0;"><strong>Phone:</strong> {obj.phone_number or 'Not set'}</p>
                    <p style="margin: 5px 0;"><strong>Role:</strong> <span style="color: {role_color}; font-weight: bold;">{obj.get_role_display()}</span></p>
                </div>
                <div>
                    <p style="margin: 5px 0;"><strong>Total Bookings:</strong> {total_bookings}</p>
                    <p style="margin: 5px 0;"><strong>Upcoming:</strong> <span style="color: #007bff;">{upcoming_bookings}</span></p>
                    <p style="margin: 5px 0;"><strong>Completed:</strong> <span style="color: #6c757d;">{completed_bookings}</span></p>
                    <p style="margin: 5px 0;"><strong>Cancelled:</strong> <span style="color: #dc3545;">{cancelled_bookings}</span></p>
                </div>
            </div>
        </div>
        """
        return mark_safe(html)

    get_profile_summary.short_description = "Profile Summary"
