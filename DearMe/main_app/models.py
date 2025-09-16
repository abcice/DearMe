from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMessage
import brevo_python
from brevo_python.rest import ApiException
import os
from django.conf import settings


# Create your models here.
class CustomUser(AbstractUser):
    birthday = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    is_email_verified = models.BooleanField(default=False)

    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    

class Letter(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("locked", "Locked"),
        ("delivered", "Delivered"),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_letters"
    )

    receivers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="received_letters",
        blank=True
    )

    external_emails = models.TextField(
        blank=True,
        help_text="Comma-separated emails for people outside the app"
    )

    subject = models.CharField(max_length=255)
    body = models.TextField()

    attachment = models.FileField(
        upload_to="letter_attachments/",
        null=True,
        blank=True
    )

    delivery_date = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    locked_at = models.DateTimeField(null=True, blank=True)

    grace_period_hours = models.IntegerField(default=48)

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
            sender={
                        "name": "DearMe App",
                        "email": os.getenv("BREVO_SENDER_EMAIL", settings.BREVO_SENDER_EMAIL)
                    },
            subject=self.subject,
            html_content=self.body
        )

        if self.attachment:
            with open(self.attachment.path, "rb") as f:
                import base64
                send_smtp_email.attachment = [
                    {
                        "content": base64.b64encode(f.read()).decode(),
                        "name": self.attachment.name.split("/")[-1]
                    }
                ]

        try:
            response = api_instance.send_transac_email(send_smtp_email)
            print(response)
            self.status = "delivered"
            self.save()
            return True
        except ApiException as e:
            print(f"Brevo error: {e}")
            return False
