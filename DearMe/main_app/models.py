from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    birthday = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')

    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()