"""
Forms for booking management.
"""

from django import forms
from .models import Booking
from karts.models import Kart


class BookingForm(forms.ModelForm):
    """
    Form for creating a new booking.
    Allows driver to optionally select a preferred kart number.
    """

    class Meta:
        model = Booking
        fields = ("chosen_kart_number", "driver_notes")
        widgets = {
            "chosen_kart_number": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Preferred kart number (optional)", "min": 1, "max": 99}
            ),
            "driver_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Any special requirements or notes (optional)",
                    "rows": 3,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form and get available karts for help text."""
        super().__init__(*args, **kwargs)
        self.fields["chosen_kart_number"].required = False
        self.fields["driver_notes"].required = False

        # Get list of active karts for help text
        active_karts = Kart.objects.filter(status="ACTIVE").values_list("number", flat=True)
        if active_karts:
            kart_list = ", ".join(str(k) for k in sorted(active_karts))
            self.fields["chosen_kart_number"].help_text = f"Available karts: {kart_list}"
        else:
            self.fields["chosen_kart_number"].help_text = "No karts currently available"

    def clean_chosen_kart_number(self):
        """Validate chosen kart exists and is active."""
        kart_number = self.cleaned_data.get("chosen_kart_number")
        if kart_number:
            try:
                kart = Kart.objects.get(number=kart_number)
                if not kart.is_available():
                    raise forms.ValidationError(
                        f"Kart #{kart_number} is currently in maintenance. "
                        "Please choose another kart or leave blank for automatic assignment."
                    )
            except Kart.DoesNotExist:
                raise forms.ValidationError(
                    f"Kart #{kart_number} does not exist. " "Please choose from the available karts."
                )
        return kart_number
