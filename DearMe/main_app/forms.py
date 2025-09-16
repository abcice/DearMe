from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
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
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already in use. Please choose another.")
        return email

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Username or Email")

    def clean(self):
        username_or_email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username_or_email and password:
            # check if email
            if "@" in username_or_email:
                try:
                    user_obj = CustomUser.objects.get(email__iexact=username_or_email)
                    username = user_obj.username
                except CustomUser.DoesNotExist:
                    raise forms.ValidationError("Invalid email or password.")
            else:
                username = username_or_email

            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("Invalid login credentials.")

            # check if email verified
            if not self.user_cache.is_email_verified:
                raise forms.ValidationError(
                    "Your email is not verified. Please check your inbox."
                )

        return self.cleaned_data
