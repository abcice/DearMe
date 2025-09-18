from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Tag, Location, Memory, DailyDiary, Letter


# ----------------------------
# Custom User Admin
# ----------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': (
                'birthday',
                'profile_picture',
                'timezone',
                'is_email_verified',
                'hide_name',
            )
        }),
    )
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_superuser', 'is_email_verified'
    )
    search_fields = ('username', 'email')


# ----------------------------
# Tag Admin
# ----------------------------
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


# ----------------------------
# Location Admin
# ----------------------------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'created_at')
    search_fields = ('name', 'city', 'country')


# ----------------------------
# Memory Admin
# ----------------------------
@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'memory_type', 'memory_date', 'is_private', 'take_to_grave')
    list_filter = ('memory_type', 'is_private', 'take_to_grave', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    date_hierarchy = 'memory_date'


# ----------------------------
# DailyDiary Admin
# ----------------------------
@admin.register(DailyDiary)
class DailyDiaryAdmin(admin.ModelAdmin):
    list_display = ('owner', 'entry_date', 'take_to_grave', 'created_at')
    list_filter = ('take_to_grave', 'created_at')
    search_fields = ('owner__username', 'text')
    date_hierarchy = 'entry_date'


# ----------------------------
# Letter Admin
# ----------------------------
@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'status', 'delivery_date', 'created_at')
    list_filter = ('status', 'delivery_date', 'created_at')
    search_fields = ('subject', 'body', 'sender__username', 'external_emails')
    date_hierarchy = 'delivery_date'
