from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Letter


admin.site.register(User, UserAdmin)
admin.site.register(Letter)

