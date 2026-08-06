from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["author", "family", "created_at"]
    list_filter = ["family"]
    search_fields = ["content", "author__email"]
    readonly_fields = ["created_at", "updated_at"]