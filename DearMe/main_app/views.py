from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView 
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils import timezone
from .models import Letter
from .forms import LetterForm
from django.contrib import messages



class Home(LoginView):
    template_name = 'home.html'

def about(request):
    return render(request, 'about.html')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('about') # don't forget to adjust it later
        
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

def profile(request):
    return render(request, 'profile.html')

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
            letter.status = "draft"
            letter.save()
            form.save_m2m()  # save receivers
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
            form.save()
            return redirect("letter_detail", pk=letter.pk)
    else:
        form = LetterForm(instance=letter)
    return render(request, "letters/letter_form.html", {"form": form})

@login_required
def send_letter(request, pk):
    letter = get_object_or_404(Letter, pk=pk, sender=request.user)

    if letter.send_email():
        messages.success(request, "Letter sent successfully!")
    else:
        messages.error(request, "No recipients found for this letter.")

    return redirect("letter_detail", pk=letter.pk)