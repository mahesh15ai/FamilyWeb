from django.contrib import admin

from .models import Relationship


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ["from_member", "relationship_type", "to_member", "created_by", "created_at"]
    list_filter = ["relationship_type"]
    search_fields = ["from_member__user__email", "to_member__user__email"]
    readonly_fields = ["created_at", "updated_at"]