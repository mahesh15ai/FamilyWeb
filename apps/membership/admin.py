from django.contrib import admin

from .models import FamilyMembership


@admin.register(FamilyMembership)
class FamilyMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "family", "role", "joined_at"]
    list_filter = ["role"]
    search_fields = ["user__email", "family__name"]
    readonly_fields = ["joined_at", "updated_at"]