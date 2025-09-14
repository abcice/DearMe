from django import forms
from .models import Letter

class LetterForm(forms.ModelForm):
    class Meta:
        model = Letter
        fields = [
            "subject",
            "body",
            "delivery_date",
            "attachment",
            "receivers",
            "external_emails",
            "grace_period_hours",
        ]
