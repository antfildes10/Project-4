"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    """Inline admin for Profile model within User admin."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone_number')


class UserAdmin(BaseUserAdmin):
    """Extended User admin with Profile inline."""
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')

    def get_role(self, obj):
        """Display user role from profile."""
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else 'N/A'
    get_role.short_description = 'Role'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model."""
    list_display = ('user', 'role', 'phone_number', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('role', 'phone_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
