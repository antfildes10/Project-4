"""
Admin configuration for karts app.
"""
from django.contrib import admin
from .models import Kart


@admin.register(Kart)
class KartAdmin(admin.ModelAdmin):
    """Admin interface for Kart model."""
    list_display = ('number', 'status', 'get_availability_icon', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('number', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('number',)

    fieldsets = (
        ('Kart Details', {
            'fields': ('number', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_availability_icon(self, obj):
        """Display availability icon."""
        if obj.is_available():
            return ' Available'
        return '=' Maintenance'
    get_availability_icon.short_description = 'Availability'

    actions = ['mark_active', 'mark_maintenance']

    def mark_active(self, request, queryset):
        """Bulk action to mark karts as active."""
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} kart(s) marked as active.')
    mark_active.short_description = 'Mark selected karts as Active'

    def mark_maintenance(self, request, queryset):
        """Bulk action to mark karts in maintenance."""
        updated = queryset.update(status='MAINTENANCE')
        self.message_user(request, f'{updated} kart(s) marked as maintenance.')
    mark_maintenance.short_description = 'Mark selected karts as Maintenance'
