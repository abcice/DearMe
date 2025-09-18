from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView 
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils import timezone
from .models import Letter, CustomUser, Memory, DailyDiary
from .forms import LetterForm, CustomUserCreationForm, EmailOrUsernameAuthenticationForm, ProfileForm, MemoryForm, DailyDiaryForm
from django.contrib import messages
import brevo_python
from brevo_python.rest import ApiException
import os
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .utils import generate_email_token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from datetime import timedelta, date
from django.contrib.auth import logout
from django.db.models import Q
import random




class Home(LoginView):
    template_name = 'home.html'
    authentication_form = EmailOrUsernameAuthenticationForm


def about(request):
    return render(request, 'about.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            token = generate_email_token(user.id)
            verification_link = request.build_absolute_uri(
                reverse('verify_email', args=[token])
            )

            subject = "Verify your DearMe account"
            message = f"""
            Hi {user.username},<br><br>
            Please verify your email by clicking this link:<br>
            <a href="{verification_link}">{verification_link}</a><br><br>
            This link will expire in 24 hours.
            """

            configuration = brevo_python.Configuration()
            configuration.api_key['api-key'] = settings.BREVO_API_KEY
            api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))

            send_smtp_email = brevo_python.SendSmtpEmail(
                to=[{"email": user.email}],
                sender={"name": "DearMe App", "email": settings.BREVO_SENDER_EMAIL},
                subject=subject,
                html_content=message
            )

            try:
                api_instance.send_transac_email(send_smtp_email)
                messages.success(
                    request,
                    "We've sent you an email with a verification link. "
                    "Please check your inbox and spam/junk folder."
                )
            except ApiException as e:
                messages.error(request, "Could not send verification email. Try again later.")
                print(f"Brevo error: {e}")

            return render(request, 'check_email.html', {'email': user.email})
        else:
            # Form invalid: either username/password issues or email already exists
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})



def verify_email(request, token):
    from .utils import verify_email_token

    user_id = verify_email_token(token)
    if user_id:
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_active = True
        user.is_email_verified = True
        user.save()
        messages.success(request, "Your email is verified! You can now log in.")
        return redirect('home')
    else:
        return HttpResponse("Invalid or expired verification link.")



@login_required
def dashboard(request):
    features = [
        {
            "title": "Letters",
            "description": "Create, edit, and send letters to anyone.",
            "url_name": "letter_list",
        },
        {
            "title": "Memories",
            "description": "Create, view, and relive your personal memories.",
            "url_name": "memory_list",
        },
        {
            "title": "Daily Diary",
            "description": "Write your thoughts and reflections every day.",
            "url_name": "diary_list",
        },
        {
            "title": "I'm Sad",
            "description": "Get a random happy memory to lift your mood.",
            "url_name": "random_happy_memory",
        },
    ]
    return render(request, "dashboard.html", {"features": features})


@login_required
def letter_list(request):
    letters = Letter.objects.filter(sender=request.user).order_by("-created_at")
    return render(request, "letters/letter_list.html", {"letters": letters})

@login_required
def letter_detail(request, pk):
    letter = get_object_or_404(Letter, pk=pk, sender=request.user)
    return render(request, "letters/letter_detail.html", {"letter": letter})

@login_required
def letter_create(request):
    if request.method == "POST":
        form = LetterForm(request.POST, request.FILES)
        if form.is_valid():
            letter = form.save(commit=False)
            letter.sender = request.user
            letter.status = "scheduled"
            letter.save()
            form.save_m2m()  
            

            messages.success(request, "Letter scheduled successfully!")
            return redirect("letter_list")
    else:
        form = LetterForm()
    return render(request, "letters/letter_form.html", {"form": form})


@login_required
def letter_edit(request, pk):
    letter = get_object_or_404(Letter, pk=pk, sender=request.user)

    if not letter.is_editable():
        return render(request, "letters/locked.html", {"letter": letter})

    if request.method == "POST":
        form = LetterForm(request.POST, request.FILES, instance=letter)
        if form.is_valid():
            letter = form.save(commit=False)
            letter.status = "scheduled"
            letter.save()
            form.save_m2m()


            messages.success(request, "Letter updated and rescheduled!")
            return redirect("letter_detail", pk=letter.pk)
    else:
        form = LetterForm(instance=letter)
    return render(request, "letters/letter_form.html", {"form": form})


@login_required
def send_letter(request, pk):
    letter = get_object_or_404(Letter, pk=pk, sender=request.user)

    if letter.send_email_brevo():
        messages.success(request, "Letter sent successfully via Brevo!")
    else:
        messages.error(request, "No recipients found or failed to send email.")

    return redirect("letter_detail", pk=letter.pk)


User = get_user_model()

def forgot_password(request):
    message_sent = False
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email__iexact=email)  
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                reverse('reset_password', kwargs={'uidb64': uid, 'token': token})  
            )
            subject = "Reset your DearMe password"
            message = f"""
            Hi {user.username},<br><br>
            You requested a password reset.<br>
            Click this link to set a new password:<br>
            <a href="{reset_link}">{reset_link}</a><br><br>
            This link will expire in 24 hours.
            """

            configuration = brevo_python.Configuration()
            configuration.api_key['api-key'] = settings.BREVO_API_KEY
            api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))
            send_smtp_email = brevo_python.SendSmtpEmail(
                to=[{"email": user.email}],
                sender={"name": "DearMe App", "email": settings.BREVO_SENDER_EMAIL},
                subject=subject,
                html_content=message
            )
            try:
                api_instance.send_transac_email(send_smtp_email)
                messages.success(request, "Check your email for the password reset link.")
                message_sent = True
            except ApiException as e:
                messages.error(request, "Could not send email. Try again later.")
                print(f"Brevo error: {e}")

        except User.DoesNotExist:
            messages.error(request, "No user exists with this email or it is typed incorrectly.")

    return render(request, 'forgot_password.html', {'message_sent': message_sent})


@login_required
def profile(request):
    user = request.user
    age = None
    if user.birthday:
        today = date.today()
        age = today.year - user.birthday.year - ((today.month, today.day) < (user.birthday.month, user.birthday.day))

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile_view")
    else:
        form = ProfileForm(instance=user)

    context = {
        "form": form,
        "user_obj": user,
        "age": age,
    }
    return render(request, "profile_edit.html", context)

@login_required
def profile_view(request):
    user = request.user
    age = None
    if user.birthday:
        today = date.today()
        age = today.year - user.birthday.year - ((today.month, today.day) < (user.birthday.month, user.birthday.day))
    return render(request, "profile_view.html", {"age": age})

@login_required
def delete_profile(request):
    if request.method == "POST":
        user = request.user
        logout(request)  # log the user out first
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect("home")
    return redirect("edit_profile")



@login_required
def memory_list(request):
    memories = Memory.objects.filter(owner=request.user)
    return render(request, "memories/memory_list.html", {"memories": memories})


@login_required
def memory_detail(request, pk):
    memory = get_object_or_404(Memory, pk=pk, owner=request.user)
    return render(request, "memories/memory_detail.html", {"memory": memory})


@login_required
def memory_create(request):
    if request.method == "POST":
        form = MemoryForm(request.POST, request.FILES)
        if form.is_valid():
            memory = form.save(commit=False)
            memory.owner = request.user
            memory.save()
            form.save_m2m()
            messages.success(request, "Memory saved successfully!")
            return redirect("memory_list")
    else:
        form = MemoryForm()
    return render(request, "memories/memory_form.html", {"form": form})


@login_required
def memory_edit(request, pk):
    memory = get_object_or_404(Memory, pk=pk, owner=request.user)
    if request.method == "POST":
        form = MemoryForm(request.POST, request.FILES, instance=memory)
        if form.is_valid():
            form.save()
            messages.success(request, "Memory updated successfully!")
            return redirect("memory_detail", pk=pk)
    else:
        form = MemoryForm(instance=memory)
    return render(request, "memories/memory_form.html", {"form": form})


@login_required
def memory_delete(request, pk):
    memory = get_object_or_404(Memory, pk=pk, owner=request.user)
    if request.method == "POST":
        memory.delete()
        messages.success(request, "Memory deleted.")
        return redirect("memory_list")
    return render(request, "memories/memory_confirm_delete.html", {"memory": memory})


# Random happy memory (for "I'm sad" button)
@login_required
def random_happy_memory(request):
    memories = Memory.objects.filter(owner=request.user, memory_type="happy")
    if memories:
        memory = random.choice(memories)
        # Pass view_only=True so template knows to hide edit/delete
        return render(request, "memories/memory_detail.html", {"memory": memory, "view_only": True})
    messages.info(request, "No happy memories found. Create one first!")
    return redirect("memory_list")



# Filter by emotion
@login_required
def memory_by_type(request, memory_type):
    memories = Memory.objects.filter(owner=request.user, memory_type=memory_type)
    return render(request, "memories/memory_list.html", {"memories": memories, "filter": memory_type})


# Filter by location
@login_required
def memory_by_location(request, location_id):
    memories = Memory.objects.filter(owner=request.user, location_id=location_id)
    return render(request, "memories/memory_list.html", {"memories": memories, "filter": "location"})


# Filter by date
@login_required
def memory_by_date(request, date_str):
    memories = Memory.objects.filter(owner=request.user, memory_date=date_str)
    return render(request, "memories/memory_list.html", {"memories": memories, "filter": date_str})

# -------------------
# Daily Diary Views
# -------------------

@login_required
def diary_list(request):
    diaries = DailyDiary.objects.filter(owner=request.user)
    return render(request, "diary/diary_list.html", {"diaries": diaries})


@login_required
def diary_detail(request, pk):
    diary = get_object_or_404(DailyDiary, pk=pk, owner=request.user)
    return render(request, "diary/diary_detail.html", {"diary": diary})

@login_required
def diary_create(request):
    if request.method == "POST":
        form = DailyDiaryForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            diary = form.save()  # save() will handle owner and locations
            messages.success(request, "Diary entry created successfully!")
            return redirect("diary_list")
    else:
        form = DailyDiaryForm(user=request.user)
    return render(request, "diary/diary_form.html", {"form": form})


@login_required
def diary_edit(request, pk):
    diary = get_object_or_404(DailyDiary, pk=pk, owner=request.user)
    if request.method == "POST":
        form = DailyDiaryForm(request.POST, request.FILES, instance=diary, user=request.user)
        if form.is_valid():
            diary = form.save(commit=False)
            # Update photo if a new one is uploaded
            if request.FILES.get("photo"):
                diary.photo = request.FILES.get("photo")
            diary.save()
            messages.success(request, "Diary entry updated successfully!")
            return redirect("diary_detail", pk=pk)
    else:
        form = DailyDiaryForm(instance=diary, user=request.user)
    return render(request, "diary/diary_form.html", {"form": form})



@login_required
def diary_delete(request, pk):
    diary = get_object_or_404(DailyDiary, pk=pk, owner=request.user)
    if request.method == "POST":
        diary.delete()
        messages.success(request, "Diary entry deleted.")
        return redirect("diary_list")
    return render(request, "diary/diary_confirm_delete.html", {"diary": diary})