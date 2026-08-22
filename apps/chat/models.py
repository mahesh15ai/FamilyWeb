from django.db import models
from django.conf import settings
from apps.families.models import Family


class ChatRoom(models.Model):
    ROOM_TYPES = (
        ("group", "Family Group"),
        ("direct", "Direct Message"),
    )

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="chat_rooms")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default="group")
    name = models.CharField(max_length=150, blank=True, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chat_rooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name or f"Chat #{self.id} ({self.room_type})"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    reply_to = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies")
    content = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="chat_images/%Y/%m/", blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.email}: {self.content[:30]}"