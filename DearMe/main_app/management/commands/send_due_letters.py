from django.core.management.base import BaseCommand
from django.utils import timezone
from main_app.models import Letter

class Command(BaseCommand):
    help = "Send letters that are due"

    def handle(self, *args, **kwargs):
        due_letters = Letter.objects.filter(status='scheduled', delivery_date__lte=timezone.now())
        for letter in due_letters:
            if letter.send_email_brevo():
                self.stdout.write(self.style.SUCCESS(f"Letter {letter.pk} sent successfully"))
            else:
                self.stdout.write(self.style.ERROR(f"Letter {letter.pk} failed to send"))
