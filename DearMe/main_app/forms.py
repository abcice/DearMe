from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import Letter, CustomUser, Memory, DailyDiary, DiaryPhoto, Tag, Location
from django.forms import FileInput
from django.utils.text import slugify

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


class ProfileForm(forms.ModelForm):
    birthday = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "text", "class": "form-control datepicker-icon"})
    )
    profile_picture = forms.ImageField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    hide_name = forms.BooleanField(required=False, label="Hide my name")

    class Meta:
        model = CustomUser
        fields = ["username", "email", "first_name", "last_name", "hide_name", "birthday", "profile_picture"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user = self.instance
        if CustomUser.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


from django import forms
from .models import Memory, Tag, Location

class MemoryForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Add tags... #tag1 #tag2",
            "class": "tags-input"
        }),
        help_text="Type tags and press enter. Suggestions will appear while typing."
    )
    location_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Add a location",
            "class": "location-input"
        }),
        help_text="Start typing a location for suggestions."
    )

    class Meta:
        model = Memory
        fields = [
            "title",
            "description",
            "memory_type",
            "tags_input",
            "location_input",
            "take_to_grave",
            "photo",
            "audio",
            "memory_date",
        ]
        widgets = {
            "memory_date": forms.DateInput(attrs={
                "type": "date",
                "class": "calendar-input"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags_input'].initial = ' '.join(f"#{t.name}" for t in self.instance.tags.all())
            if self.instance.location:
                self.fields['location_input'].initial = self.instance.location.name

    def clean_tags_input(self):
        """Convert user input into Tag objects."""
        tags_str = self.cleaned_data.get("tags_input", "")
        tags_list = [t.strip().lstrip('#') for t in tags_str.split() if t.strip()]
        tags_objs = []
        for t in tags_list:
            tag, _ = Tag.objects.get_or_create(name__iexact=t, defaults={"name": t})
            tags_objs.append(tag)
        return tags_objs

    def clean_location_input(self):
        """Get or create a Location object (case-insensitive)."""
        loc_str = self.cleaned_data.get("location_input", "").strip()
        if not loc_str:
            return None
        loc_obj, _ = Location.objects.get_or_create(name__iexact=loc_str, defaults={"name": loc_str})
        return loc_obj

    def save(self, commit=True):
        memory = super().save(commit=False)
        memory.location = self.cleaned_data.get('location_input')
        if commit:
            memory.save()
            memory.tags.set(self.cleaned_data.get('tags_input', []))
        return memory


class DailyDiaryForm(forms.ModelForm):
    memories = forms.ModelMultipleChoiceField(
        queryset=Memory.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select memories to include in this diary entry"
    )

    photos = forms.FileField(
        required=False,
        help_text="Upload one or more photos"
    )


    class Meta:
        model = DailyDiary
        fields = [
            "entry_date",
            "text",
            "memories",
            "photos",
            "audio",
            "favorite_music",
            "favorite_foods",
            "favorite_shows",
            "take_to_grave",
            "locations",
        ]
        widgets = {
            "entry_date": forms.DateInput(attrs={"type": "date"}),
            "text": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["memories"].queryset = Memory.objects.filter(owner=user)

    def save(self, commit=True):
        diary = super().save(commit=commit)
        
        # Handle multiple photos
        if self.files.getlist("photos"):
            for photo_file in self.files.getlist("photos"):
                DiaryPhoto.objects.create(diary=diary, image=photo_file)
        
        return diary