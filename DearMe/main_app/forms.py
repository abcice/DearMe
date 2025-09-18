from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import Letter, CustomUser, Memory, DailyDiary, Tag, Location


# -----------------------
# Letter Form
# -----------------------
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
            "memories",
            "diary_entries",
        ]
        widgets = {
            "delivery_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
        }

    def save(self, commit=True):
        # Save basic letter
        letter = super().save(commit=False)

        # Ensure sender is set before saving
        if not letter.sender_id and hasattr(self, 'user'):
            letter.sender = self.user

        if commit:
            letter.save()
            self.save_m2m()  # save normal M2M fields

            # Attach memories
            memory_ids = self.data.get("selected_memories", "")
            if memory_ids:
                ids_list = [int(mid) for mid in memory_ids.split(",") if mid.isdigit()]
                letter.memories.set(Memory.objects.filter(id__in=ids_list, owner=letter.sender))
            else:
                letter.memories.clear()

            # Attach diaries
            diary_ids = self.data.get("selected_diaries", "")
            if diary_ids:
                ids_list = [int(did) for did in diary_ids.split(",") if did.isdigit()]
                letter.diary_entries.set(DailyDiary.objects.filter(id__in=ids_list, owner=letter.sender))
            else:
                letter.diary_entries.clear()

                

        return letter



# -----------------------
# User Forms
# -----------------------
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birthday = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

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

            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid login credentials.")

            if not self.user_cache.is_email_verified:
                raise forms.ValidationError("Your email is not verified. Please check your inbox.")

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


# -----------------------
# Memory Form
# -----------------------
class MemoryForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Add tags... #tag1 #tag2", "class": "tags-input"}),
        help_text="Type tags and press enter. Suggestions will appear while typing."
    )
    location_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Add a location", "class": "location-input"}),
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
            "memory_date": forms.DateInput(attrs={"type": "date", "class": "calendar-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags_input'].initial = ' '.join(f"#{t.name}" for t in self.instance.tags.all())
            if self.instance.location:
                self.fields['location_input'].initial = self.instance.location.name

    def clean_tags_input(self):
        tags_str = self.cleaned_data.get("tags_input", "")
        tags_list = [t.strip().lstrip('#') for t in tags_str.split() if t.strip()]
        tags_objs = []
        for t in tags_list:
            tag, _ = Tag.objects.get_or_create(name__iexact=t, defaults={"name": t})
            tags_objs.append(tag)
        return tags_objs

    def clean_location_input(self):
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


# -----------------------
# Daily Diary Form
# -----------------------
class DailyDiaryForm(forms.ModelForm):
    photo = forms.ImageField(required=False, label="Photo")
    locations_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Enter locations...", "class": "location-input"}),
        help_text="You can type multiple locations separated by commas."
    )

    class Meta:
        model = DailyDiary
        fields = [
            "entry_date",
            "text",
            "memories",
            "audio",
            "photo",
            "favorite_music",
            "favorite_foods",
            "favorite_shows",
            "take_to_grave",
        ]
        widgets = {
            "entry_date": forms.DateInput(attrs={"type": "date"}),
            "text": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Filter memories to the current user
        if self.user:
            self.fields["memories"].queryset = Memory.objects.filter(owner=self.user)

        # Pre-fill locations if editing
        if self.instance.pk and self.instance.locations.exists():
            self.fields['locations_input'].initial = ', '.join(loc.name for loc in self.instance.locations.all())
        if self.instance.pk and self.instance.photo:
            self.fields['photo'].initial = self.instance.photo

    def save(self, commit=True):
        diary = super().save(commit=False)

        if getattr(diary, "owner_id", None) is None and self.user:
            diary.owner = self.user

        diary.save()  # Save first to get an ID

        # Handle locations
        loc_str = self.cleaned_data.get("locations_input", "")
        loc_names = [l.strip() for l in loc_str.split(",") if l.strip()]
        diary.locations.set([])  # clear first
        for loc_name in loc_names:
            loc_obj, _ = Location.objects.get_or_create(
                name__iexact=loc_name, defaults={"name": loc_name}
            )
            diary.locations.add(loc_obj)

        # Handle attached memories
        memory_ids = self.data.get("selected_memories", "")
        if memory_ids:
            ids_list = [int(mid) for mid in memory_ids.split(",") if mid.isdigit()]
            diary.memories.set(Memory.objects.filter(id__in=ids_list, owner=self.user))
        else:
            diary.memories.clear()

        return diary
