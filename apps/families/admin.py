from django.contrib import admin

from .models import Family


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ["name", "family_code", "created_by", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "family_code"]
    readonly_fields = ["uuid", "family_code", "created_at", "updated_at"]