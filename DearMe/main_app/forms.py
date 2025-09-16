from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Letter, CustomUser

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
        widgets = {
            "delivery_date": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",  
                    "class": "form-control",
                }
            ),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "birthday", "password1", "password2")