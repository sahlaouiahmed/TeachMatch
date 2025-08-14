from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "first_name", "last_name", "country", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "country")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)