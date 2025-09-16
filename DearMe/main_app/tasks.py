from celery import shared_task
from django.utils import timezone
from .models import Letter

@shared_task
def send_due_letters():
    """
    Find all letters that are scheduled and due,
    send them via email, and mark as delivered.
    """
    due_letters = Letter.objects.filter(status='scheduled', delivery_date__lte=timezone.now())
    for letter in due_letters:
        if letter.send_email_brevo():
            print(f"Letter {letter.pk} sent successfully.")
        else:
            print(f"Letter {letter.pk} failed to send.")

@shared_task
def send_letter_task(letter_id):
    try:
        letter = Letter.objects.get(pk=letter_id)
        if letter.send_email_brevo():
            letter.status = "delivered"
            letter.save()
    except Letter.DoesNotExist:
        print(f"Letter {letter_id} not found.")