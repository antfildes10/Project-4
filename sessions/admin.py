"""
Admin configuration for sessions app.
"""
from django.contrib import admin
from .models import Track, SessionSlot


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    """Admin interface for Track model."""
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'address', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Track Information', {
            'fields': ('name', 'address', 'phone', 'email')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Internal Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SessionSlot)
class SessionSlotAdmin(admin.ModelAdmin):
    """Admin interface for SessionSlot model."""
    list_display = (
        'get_session_name',
        'session_type',
        'start_datetime',
        'end_datetime',
        'capacity',
        'get_booked_count',
        'get_available_spots',
        'price'
    )
    list_filter = ('session_type', 'start_datetime', 'track')
    search_fields = ('description',)
    readonly_fields = ('created_at', 'updated_at', 'get_booked_count', 'get_available_spots')
    date_hierarchy = 'start_datetime'
    ordering = ('-start_datetime',)

    fieldsets = (
        ('Session Details', {
            'fields': ('track', 'session_type', 'start_datetime', 'end_datetime')
        }),
        ('Capacity & Pricing', {
            'fields': ('capacity', 'price', 'get_booked_count', 'get_available_spots')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_session_name(self, obj):
        """Display session type and date."""
        return str(obj)
    get_session_name.short_description = 'Session'

    def get_booked_count(self, obj):
        """Display count of confirmed/pending bookings."""
        count = obj.bookings.filter(status__in=['PENDING', 'CONFIRMED']).count()
        if count >= obj.capacity:
            return f'{count} (FULL)'
        return count
    get_booked_count.short_description = 'Booked'

    def get_available_spots(self, obj):
        """Display available spots."""
        available = obj.get_available_spots()
        if available <= 0:
            return '0 (FULL)'
        return available
    get_available_spots.short_description = 'Available'
