from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from encrypted_model_fields.fields import EncryptedTextField
import uuid
import os
import brevo_python
from brevo_python.rest import ApiException
import base64
from django.utils.text import slugify


# ----------------------------
# Helper functions for file uploads
# ----------------------------
def profile_pic_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_pics', filename)


def memory_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('memories_files', filename)


def diary_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('diary_files', filename)


# ----------------------------
# Custom User
# ----------------------------
class CustomUser(AbstractUser):
    birthday = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to=profile_pic_path, null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    is_email_verified = models.BooleanField(default=False)
    hide_name = models.BooleanField(default=False)

    def full_name(self):
        if self.hide_name:
            return ""
        return f"{self.first_name} {self.last_name}".strip()


# ----------------------------
# Tag Model
# ----------------------------
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ----------------------------
# Location Model
# ----------------------------
class Location(models.Model):
    name = models.CharField(max_length=255)  # e.g., "Paris"
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        parts = [self.name]
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


# ----------------------------
# Memory Model
# ----------------------------
class Memory(models.Model):
    MEMORY_TYPE_CHOICES = [
        ("happy", "Happy"),
        ("sad", "Sad"),
        ("funny", "Funny"),
        ("travel", "Travel"),
        ("achievement", "Achievement"),
        ("family", "Family"),
        ("romantic", "Romantic"),
        ("other", "Other"),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memories")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    memory_type = models.CharField(max_length=50, choices=MEMORY_TYPE_CHOICES, default="happy")
    tags = models.ManyToManyField("Tag", blank=True, related_name="memories")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name="memories")
    is_private = models.BooleanField(default=True, help_text="Memory is private by default")
    take_to_grave = models.BooleanField(default=False, help_text="Memory won't be shared after death")
    photo = models.ImageField(upload_to=memory_file_path, null=True, blank=True)
    audio = models.FileField(upload_to=memory_file_path, null=True, blank=True)
    video = models.FileField(upload_to=memory_file_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    memory_date = models.DateField(default=timezone.now)
    

    def __str__(self):
        return f"{self.title} ({self.get_memory_type_display()})"

    class Meta:
        ordering = ['-memory_date', '-created_at']


# ----------------------------
# Daily Diary Model
# ----------------------------
class DailyDiary(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diary_entries")
    entry_date = models.DateField()
    text = EncryptedTextField(blank=True)
    memories = models.ManyToManyField(Memory, blank=True, related_name="included_in_diaries")
    audio = models.FileField(upload_to=diary_file_path, null=True, blank=True)
    favorite_music = EncryptedTextField(blank=True, help_text="Optional: list your favorite music or upload an MP3 file")
    favorite_foods = EncryptedTextField(blank=True, help_text="Optional: list your favorite foods")
    favorite_shows = EncryptedTextField(blank=True, help_text="Optional: list your favorite anime/TV shows or add links")
    take_to_grave = models.BooleanField(default=False, help_text="Diary won't be shared after death")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    locations = models.ManyToManyField(Location, blank=True, related_name="diary_entries")
    

    class Meta:
        unique_together = ("owner", "entry_date")
        ordering = ['-entry_date']

    def __str__(self):
        return f"Diary entry for {self.entry_date} by {self.owner.username}"
    
class DiaryPhoto(models.Model):
    diary = models.ForeignKey("DailyDiary", on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to=diary_file_path)

    def __str__(self):
        return f"Photo for {self.diary.entry_date}"



# ----------------------------
# Letter Model
# ----------------------------
class Letter(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("locked", "Locked"),
        ("delivered", "Delivered"),
    ]

    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_letters")
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="received_letters", blank=True)
    external_emails = models.TextField(blank=True, help_text="Comma-separated emails for people outside the app")
    subject = models.CharField(max_length=255)
    body = models.TextField()
    attachment = models.FileField(upload_to="letter_attachments/", null=True, blank=True)
    delivery_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    locked_at = models.DateTimeField(null=True, blank=True)
    grace_period_hours = models.IntegerField(default=48)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Connect letters to memories and diaries
    memories = models.ManyToManyField(Memory, blank=True, related_name="included_in_letters")
    diary_entries = models.ManyToManyField(DailyDiary, blank=True, related_name="included_in_letters")

    def is_editable(self):
        if self.status == "draft":
            return True
        if self.status == "scheduled":
            if not self.locked_at:
                return True
            return timezone.now() < self.locked_at + timedelta(hours=self.grace_period_hours)
        return False

    def lock(self):
        self.status = "locked"
        self.locked_at = timezone.now()
        self.save()

    def is_due(self):
        return timezone.now() >= self.delivery_date

    def get_external_emails(self):
        return [email.strip() for email in self.external_emails.split(",") if email.strip()]

    def get_absolute_url(self):
        return reverse("letter_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"

    def send_email_brevo(self):
        recipients = [{"email": r.email} for r in self.receivers.all() if r.email]
        recipients += [{"email": e} for e in self.get_external_emails()]
        if not recipients:
            return False

        configuration = brevo_python.Configuration()
        configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY', settings.BREVO_API_KEY)
        api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))

        send_smtp_email = brevo_python.SendSmtpEmail(
            to=recipients,
            sender={"name": "DearMe App", "email": os.getenv("BREVO_SENDER_EMAIL", settings.BREVO_SENDER_EMAIL)},
            subject=self.subject,
            html_content=self.body
        )

        if self.attachment:
            with open(self.attachment.path, "rb") as f:
                send_smtp_email.attachment = [{
                    "content": base64.b64encode(f.read()).decode(),
                    "name": os.path.basename(self.attachment.name)
                }]

        try:
            response = api_instance.send_transac_email(send_smtp_email)
            print(response)
            self.status = "delivered"
            self.save()
            return True
        except ApiException as e:
            print(f"Brevo error: {e}")
            return False
