"""
Forms for kart management.
"""
from django import forms
from .models import Kart


class KartForm(forms.ModelForm):
    """
    Form for creating and editing karts.
    Manager-only functionality.
    """
    class Meta:
        model = Kart
        fields = ('number', 'status', 'notes')
        widgets = {
            'number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 99,
                'placeholder': 'Enter kart number (1-99)'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Internal notes about kart condition (optional)'
            })
        }

    def clean_number(self):
        """Validate kart number is unique (excluding current instance)."""
        number = self.cleaned_data.get('number')
        if number:
            # Check if another kart has this number
            existing = Kart.objects.filter(number=number)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise forms.ValidationError(
                    f'Kart #{number} already exists. Please choose a different number.'
                )

        return number
