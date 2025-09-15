from background_task import background
from .models import Letter

@background(schedule=60)  
def send_due_letters_task():
    letters = Letter.objects.filter(status__in=['draft', 'scheduled'])
    for letter in letters:
        if letter.is_due():
            if letter.send_email_brevo():
                print(f"Sent letter {letter.pk}")
