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

        # Reject if unauthenticated
        if not self.user or self.user.is_anonymous:
            logger.warning(f"Rejecting unauthenticated WebSocket for room {self.room_id}")
            await self.close(code=4001)
            return

        # Join the room channel group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get("content", "").strip()

        if not content:
            return

        saved_msg = await self.save_message(self.room_id, self.user, content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_msg,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def save_message(self, room_id, sender, content):
        room = ChatRoom.objects.get(id=room_id)
        msg = Message.objects.create(room=room, sender=sender, content=content)
        room.save()

        sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.email.split("@")[0]
        avatar_url = None
        if hasattr(sender, "avatar") and sender.avatar:
            avatar_url = sender.avatar.url

        return {
            "id": msg.id,
            "room": room.id,
            "content": msg.content,
            "image_url": None,
            "created_at": msg.created_at.isoformat(),
            "sender": {
                "id": sender.id,
                "name": sender_name,
                "email": sender.email,
                "avatar": avatar_url,
            }
        }