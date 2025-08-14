from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "first_name", "last_name", "country", "is_staff", "is_active", "is_verified")
    list_filter = ("is_staff", "is_active", "is_verified", "country")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("id",)
    fieldsets = UserAdmin.fieldsets + (
        ("Extra info", {"fields": ("phone_number","country","location","date_of_birth","gender","bio","profile_picture","role","is_verified","last_seen")}),
    )
