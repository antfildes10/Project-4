"""
Forms for core app functionality.
"""

from django import forms


class ContactForm(forms.Form):
    """
    Contact form for visitor inquiries.
    """

    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your name",
                "required": "required",
                "aria-required": "true"
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your email address",
                "autocomplete": "email",
                "required": "required",
                "aria-required": "true"
            }
        )
    )
    subject = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Subject",
                "required": "required",
                "aria-required": "true"
            }
        ),
    )
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Your message",
                "required": "required",
                "aria-required": "true"
            }
        )
    )
