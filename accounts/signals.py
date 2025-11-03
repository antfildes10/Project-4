"""
Signal handlers for automatic profile creation and role syncing.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile when a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save the Profile when the User is saved.
    """
    instance.profile.save()


@receiver(post_save, sender=Profile)
def sync_role_to_groups(sender, instance, **kwargs):
    """
    Automatically sync Profile.role to Django Groups.
    This keeps role-based permissions in sync with the simple role field.
    """
    user = instance.user

    # Remove user from all role groups
    role_groups = Group.objects.filter(name__in=["Drivers", "Managers", "Marshals"])
    user.groups.remove(*role_groups)

    # Add user to appropriate group based on their role
    role_to_group = {
        "DRIVER": "Drivers",
        "MANAGER": "Managers",
        "MARSHAL": "Marshals",
    }

    group_name = role_to_group.get(instance.role)
    if group_name:
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            # Group hasn't been created yet (migrations not run)
            pass
