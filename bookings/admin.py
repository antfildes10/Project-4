"""
Admin configuration for bookings app.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model."""
    list_display = (
        'id',
        'driver',
        'get_session_info',
        'get_status_badge',
        'assigned_kart',
        'created_at'
    )
    list_filter = ('status', 'session_slot__session_type', 'created_at')
    search_fields = (
        'driver__username',
        'driver__email',
        'session_slot__description',
        'driver_notes',
        'manager_notes'
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Booking Information', {
            'fields': ('driver', 'session_slot', 'status')
        }),
        ('Kart Assignment', {
            'fields': ('chosen_kart_number', 'assigned_kart')
        }),
        ('Notes', {
            'fields': ('driver_notes', 'manager_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['confirm_bookings', 'cancel_bookings', 'complete_bookings']

    def get_session_info(self, obj):
        """Display session information."""
        return f"{obj.session_slot.get_session_type_display()} - {obj.session_slot.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    get_session_info.short_description = 'Session'

    def get_status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'PENDING': '#FFA500',      # Orange
            'CONFIRMED': '#28a745',    # Green
            'CANCELLED': '#dc3545',    # Red
            'COMPLETED': '#6c757d',    # Gray
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'

    def confirm_bookings(self, request, queryset):
        """Bulk action to confirm pending bookings."""
        confirmed_count = 0
        for booking in queryset.filter(status='PENDING'):
            if booking.can_be_confirmed():
                # Try to assign kart
                if booking.assign_random_kart():
                    booking.status = 'CONFIRMED'
                    booking.save()
                    confirmed_count += 1
                else:
                    self.message_user(
                        request,
                        f'Booking #{booking.id}: No available karts',
                        level='warning'
                    )

        if confirmed_count:
            self.message_user(request, f'{confirmed_count} booking(s) confirmed.')
    confirm_bookings.short_description = 'Confirm selected bookings'

    def cancel_bookings(self, request, queryset):
        """Bulk action to cancel bookings."""
        cancelled_count = 0
        for booking in queryset:
            if booking.can_be_cancelled():
                booking.status = 'CANCELLED'
                booking.save()
                cancelled_count += 1

        if cancelled_count:
            self.message_user(request, f'{cancelled_count} booking(s) cancelled.')
        else:
            self.message_user(
                request,
                'No bookings could be cancelled (check if sessions have already started)',
                level='warning'
            )
    cancel_bookings.short_description = 'Cancel selected bookings'

    def complete_bookings(self, request, queryset):
        """Bulk action to mark bookings as completed."""
        completed_count = 0
        for booking in queryset.filter(status='CONFIRMED'):
            if booking.can_be_completed():
                booking.status = 'COMPLETED'
                booking.save()
                completed_count += 1

        if completed_count:
            self.message_user(request, f'{completed_count} booking(s) marked as completed.')
        else:
            self.message_user(
                request,
                'No bookings could be completed (sessions must have ended)',
                level='warning'
            )
    complete_bookings.short_description = 'Mark selected bookings as completed'
