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
from .models import Letter, CustomUser
from .forms import LetterForm, CustomUserCreationForm, EmailOrUsernameAuthenticationForm, ProfileForm
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





class Home(LoginView):
    template_name = 'home.html'
    authentication_form = EmailOrUsernameAuthenticationForm


def about(request):
    return render(request, 'about.html')

def signup(request):
    error_message = ''
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
                messages.success(request, "We've sent you an email with a verification link. "
                "Please check your inbox and junk/spam folder. "
                "Add our email to your safe senders list so you don’t miss future emails.")
            except ApiException as e:
                messages.error(request, f"Could not send verification email. Try again later.")
                print(f"Brevo error: {e}")

            return redirect('home')
        else:
            email = request.POST.get('email')
            if CustomUser.objects.filter(email__iexact=email).exists():
                messages.info(request, "Email already exists. Did you forget your password? "
                                        "You can reset it <a href='/accounts/forgot-password/'>here</a>.")
            else:
                error_message = 'Invalid sign up - try again'

    form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form, 'error_message': error_message})

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
        # future features can be added here
        # {"title": "Another Feature", "description": "Description...", "url_name": "feature_url"},
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