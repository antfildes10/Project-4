"""
Forms for user registration and profile management.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class UserRegistrationForm(UserCreationForm):
    """
    Extended user registration form with email field.
    Creates new user accounts with required email validation.
    """

    email = forms.EmailField(
        required=True, help_text="Required. Enter a valid email address."
    )
    first_name = forms.CharField(max_length=30, required=False, help_text="Optional.")
    last_name = forms.CharField(max_length=30, required=False, help_text="Optional.")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

    def clean_email(self):
        """Validate that email is unique."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email


class ProfileEditForm(forms.ModelForm):
    """
    Form for editing user profile information.
    Allows users to update their phone number.
    """

    class Meta:
        model = Profile
        fields = ("phone_number",)
        widgets = {
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter phone number"}
            )
        }


class UserEditForm(forms.ModelForm):
    """
    Form for editing basic user information.
    Allows users to update email, first name, and last name.
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        """Store the current user for email validation."""
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        """Validate that email is unique (excluding current user)."""
        email = self.cleaned_data.get("email")
        if self.user:
            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError("This email address is already in use.")
        return email
