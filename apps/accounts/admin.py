from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email", "first_name", "last_name", "is_active", "is_verified", "is_staff", "created_at"]
    list_filter = ["is_active", "is_verified", "is_staff", "gender"]
    search_fields = ["email", "first_name", "last_name", "phone_number", "uuid"]
    readonly_fields = ["uuid", "created_at", "updated_at", "last_login"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {
            "fields": (
                "first_name", "last_name", "phone_number",
                "profile_photo", "date_of_birth", "gender", "bio",
            )
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "is_verified", "groups", "user_permissions")
        }),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
        ("Identifiers", {"fields": ("uuid",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )