"""
Forms for core app functionality.
"""

from django import forms


class ContactForm(forms.Form):
    """
    Contact form for visitor inquiries.
    """

    name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your email address"})
    )
    subject = forms.CharField(
        max_length=200, widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Your message"})
    )
