from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import SessionToken, User, UserProfile, UserSettings


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "role", "account_type", "current_level", "is_active", "date_joined"]
    list_filter = ["role", "account_type", "is_active", "current_level"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("English Study", {"fields": ("role", "account_type", "current_level", "target_level", "is_deleted")}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "gender", "native_language"]
    search_fields = ["user__email", "phone"]


@admin.register(SessionToken)
class SessionTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "device_name", "ip_address", "is_revoked", "created_at"]
    list_filter = ["is_revoked"]
    search_fields = ["user__email", "ip_address"]
