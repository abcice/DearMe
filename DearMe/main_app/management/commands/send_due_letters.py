from django.core.management.base import BaseCommand
from django.utils import timezone
from main_app.models import Letter

class Command(BaseCommand):
    help = "Send letters whose delivery date has arrived"

    def handle(self, *args, **options):
        due_letters = Letter.objects.filter(status__in=["draft", "scheduled"], delivery_date__lte=timezone.now())
        count = 0
        for letter in due_letters:
            if letter.send_email_brevo():
                self.stdout.write(f"Sent letter {letter.pk} to recipients")
                count += 1
        self.stdout.write(f"Total letters sent: {count}")
