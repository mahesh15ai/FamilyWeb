import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope.get("user")

        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get("type", "chat_message")

        if event_type == "typing":
            is_typing = data.get("is_typing", False)
            sender_name = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.email.split("@")[0]
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_typing",
                    "user_id": self.user.id,
                    "user_name": sender_name,
                    "is_typing": is_typing,
                }
            )
            return

        content = data.get("content", "").strip()
        reply_to_id = data.get("reply_to_id", None)
        if not content:
            return

        saved_msg = await self.save_message(self.room_id, self.user, content, reply_to_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_msg,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"type": "chat_message", "message": event["message"]}))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, room_id, sender, content, reply_to_id=None):
        room = ChatRoom.objects.get(id=room_id)
        reply_msg = Message.objects.filter(id=reply_to_id).first() if reply_to_id else None

        msg = Message.objects.create(room=room, sender=sender, content=content, reply_to=reply_msg)
        room.save()

        sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email.split("@")[0]
        avatar_url = sender.avatar.url if hasattr(sender, "avatar") and sender.avatar else None

        reply_snippet = None
        if reply_msg:
            r_sender_name = f"{reply_msg.sender.first_name} {reply_msg.sender.last_name}".strip() or reply_msg.sender.email.split("@")[0]
            reply_snippet = {
                "id": reply_msg.id,
                "sender_name": r_sender_name,
                "content": reply_msg.content or "📷 Photo",
            }

        return {
            "id": msg.id,
            "room": room.id,
            "content": msg.content,
            "reply_to": reply_snippet,
            "image_url": None,
            "is_read": False,
            "created_at": msg.created_at.isoformat(),
            "sender": {
                "id": sender.id,
                "name": sender_name,
                "email": sender.email,
                "avatar": avatar_url,
            }
        }