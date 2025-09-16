from django.urls import path
from django.contrib.auth import views as auth_views
from . import views 

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/verify/<str:token>', views.verify_email, name="verify_email"),
    path('accounts/forgot-password/', views.forgot_password, name='forgot_password'),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='/'
        ),
        name='reset_password'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile, name='edit_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("letters/", views.letter_list, name="letter_list"),
    path("letters/<int:pk>/", views.letter_detail, name="letter_detail"),
    path("letters/new/", views.letter_create, name="letter_create"),
    path("letters/<int:pk>/edit/", views.letter_edit, name="letter_edit"),
    path("letters/<int:pk>/send/", views.send_letter, name="letter_send"),

    
]