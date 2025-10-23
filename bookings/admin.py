"""
Admin configuration for bookings app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Booking model with CRM-style features."""
    list_display = (
        'id',
        'get_driver_link',
        'get_session_link',
        'get_status_badge',
        'get_kart_badge',
        'booking_datetime',
        'get_session_date'
    )
    list_filter = (
        'status',
        'session_slot__session_type',
        ('booking_datetime', admin.DateFieldListFilter),
        ('session_slot__start_datetime', admin.DateFieldListFilter),
        'assigned_kart__status'
    )
    search_fields = (
        'id',
        'driver__username',
        'driver__email',
        'driver__first_name',
        'driver__last_name',
        'assigned_kart__number',
        'driver_notes',
        'manager_notes'
    )
    readonly_fields = ('booking_datetime', 'created_at', 'updated_at', 'get_booking_summary')
    date_hierarchy = 'booking_datetime'
    ordering = ('-booking_datetime',)
    list_per_page = 25
    list_select_related = ('driver', 'session_slot', 'assigned_kart', 'session_slot__track')

    fieldsets = (
        (None, {
            'fields': ('get_booking_summary',)
        }),
        ('Booking Information', {
            'fields': ('driver', 'session_slot', 'status')
        }),
        ('Kart Assignment', {
            'fields': ('chosen_kart_number', 'assigned_kart'),
            'description': 'Assign a kart to this booking. Leave empty for automatic assignment.'
        }),
        ('Notes', {
            'fields': ('driver_notes', 'manager_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('booking_datetime', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['confirm_bookings', 'cancel_bookings', 'complete_bookings']

    def get_driver_link(self, obj):
        """Display clickable driver link."""
        url = reverse('admin:auth_user_change', args=[obj.driver.id])
        return format_html('<a href="{}">{}</a>', url, obj.driver.username)
    get_driver_link.short_description = 'Driver'
    get_driver_link.admin_order_field = 'driver__username'

    def get_session_link(self, obj):
        """Display clickable session link with details."""
        url = reverse('admin:session_slots_sessionslot_change', args=[obj.session_slot.id])
        session_type = 'GP' if obj.session_slot.session_type == 'GRAND_PRIX' else 'Open'
        return format_html(
            '<a href="{}">{} Session</a>',
            url,
            session_type
        )
    get_session_link.short_description = 'Session Type'
    get_session_link.admin_order_field = 'session_slot__session_type'

    def get_session_date(self, obj):
        """Display session date and time."""
        return obj.session_slot.start_datetime.strftime('%d %b %Y, %H:%M')
    get_session_date.short_description = 'Session Date/Time'
    get_session_date.admin_order_field = 'session_slot__start_datetime'

    def get_kart_badge(self, obj):
        """Display kart assignment with badge."""
        if obj.assigned_kart:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">Kart #{}</span>',
                obj.assigned_kart.number
            )
        return format_html('<span style="color: #999;">Not assigned</span>')
    get_kart_badge.short_description = 'Kart'
    get_kart_badge.admin_order_field = 'assigned_kart__number'

    def get_booking_summary(self, obj):
        """Display comprehensive booking summary."""
        html = f'''
        <div style="font-family: monospace; background: #f5f5f5; padding: 15px; border-radius: 5px;">
            <h3 style="margin-top: 0;">Booking #{obj.id} Summary</h3>
            <p><strong>Driver:</strong> {obj.driver.get_full_name()} ({obj.driver.username})</p>
            <p><strong>Email:</strong> {obj.driver.email}</p>
            <p><strong>Session:</strong> {obj.session_slot.get_session_type_display()}</p>
            <p><strong>Date:</strong> {obj.session_slot.start_datetime.strftime('%A, %d %B %Y at %H:%M')}</p>
            <p><strong>Price:</strong> €{obj.session_slot.price}</p>
            <p><strong>Track:</strong> {obj.session_slot.track.name}</p>
            <p><strong>Status:</strong> {obj.get_status_display()}</p>
            {'<p><strong>Kart:</strong> #' + str(obj.assigned_kart.number) + '</p>' if obj.assigned_kart else '<p><strong>Kart:</strong> Not yet assigned</p>'}
        </div>
        '''
        return mark_safe(html)
    get_booking_summary.short_description = 'Booking Summary'

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
