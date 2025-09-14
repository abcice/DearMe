from django.urls import path
from . import views 

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path("letters/", views.letter_list, name="letter_list"),
    path("letters/<int:pk>/", views.letter_detail, name="letter_detail"),
    path("letters/new/", views.letter_create, name="letter_create"),
    path("letters/<int:pk>/edit/", views.letter_edit, name="letter_edit"),
    
]