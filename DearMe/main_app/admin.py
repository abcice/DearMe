from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Letter

# Register your custom user
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # optional: display fields
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('birthday', 'profile_picture', 'timezone', 'is_email_verified')}),
    )
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_email_verified')

# Register your Letter model
admin.site.register(Letter)
