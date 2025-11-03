"""
Forms for session slot management.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import SessionSlot


class SessionSlotForm(forms.ModelForm):
    """
    Form for creating and editing session slots.
    Manager-only functionality with validation.
    """

    class Meta:
        model = SessionSlot
        fields = (
            "track",
            "session_type",
            "start_datetime",
            "end_datetime",
            "capacity",
            "price",
            "description",
        )
        widgets = {
            "track": forms.Select(attrs={"class": "form-control"}),
            "session_type": forms.Select(attrs={"class": "form-control"}),
            "start_datetime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"}
            ),
            "capacity": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": 0}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional session description",
                }
            ),
        }

    def clean(self):
        """Validate session times and prevent past sessions."""
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get("start_datetime")
        end_datetime = cleaned_data.get("end_datetime")

        # Validate start time is in the future (for new sessions)
        if start_datetime and not self.instance.pk:
            if start_datetime < timezone.now():
                raise ValidationError(
                    {"start_datetime": "Cannot create sessions in the past."}
                )

        # Validate start is before end
        if start_datetime and end_datetime:
            if start_datetime >= end_datetime:
                raise ValidationError(
                    {"end_datetime": "End time must be after start time."}
                )

            # Validate session duration is reasonable (at least 15 minutes)
            duration = end_datetime - start_datetime
            if duration.total_seconds() < 900:  # 15 minutes
                raise ValidationError(
                    {"end_datetime": "Session must be at least 15 minutes long."}
                )

        return cleaned_data
