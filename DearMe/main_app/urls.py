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
    path("memories/", views.memory_list, name="memory_list"),
    path("memories/new/", views.memory_create, name="memory_create"),
    path("memories/<int:pk>/", views.memory_detail, name="memory_detail"),
    path("memories/<int:pk>/edit/", views.memory_edit, name="memory_edit"),
    path("memories/<int:pk>/delete/", views.memory_delete, name="memory_delete"),
    path("memories/random/happy/", views.random_happy_memory, name="random_happy_memory"),
    path("memories/type/<str:memory_type>/", views.memory_by_type, name="memory_by_type"),
    path("memories/location/<int:location_id>/", views.memory_by_location, name="memory_by_location"),
    path("memories/date/<str:date_str>/", views.memory_by_date, name="memory_by_date"),
    path("diary/", views.diary_list, name="diary_list"),
    path("diary/new/", views.diary_create, name="diary_create"),
    path("diary/<int:pk>/", views.diary_detail, name="diary_detail"),
    path("diary/<int:pk>/edit/", views.diary_edit, name="diary_edit"),
    path("diary/<int:pk>/delete/", views.diary_delete, name="diary_delete"),


    
]