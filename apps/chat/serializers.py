from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "name", "avatar"]

    def get_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.email.split("@")[0]

    def get_avatar(self, obj):
        if hasattr(obj, "avatar") and obj.avatar:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


class MessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "room", "sender", "content", "image", "image_url", "created_at"]
        read_only_fields = ["id", "sender", "created_at"]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserBriefSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    display_avatar = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            "id",
            "family",
            "room_type",
            "name",
            "display_name",
            "display_avatar",
            "participants",
            "last_message",
            "created_at",
            "updated_at",
        ]

    def get_last_message(self, obj):
        msg = obj.messages.order_by("-created_at").first()
        if not msg:
            return None
        sender_name = f"{msg.sender.first_name} {msg.sender.last_name}".strip() or msg.sender.email.split("@")[0]
        return {
            "content": msg.content or "📷 Sent an image",
            "sender_name": sender_name,
            "created_at": msg.created_at,
        }

    def get_display_name(self, obj):
        if obj.room_type == "group":
            return obj.name or f"{obj.family.name} General"
        request = self.context.get("request")
        if request and request.user:
            other = obj.participants.exclude(id=request.user.id).first()
            if other:
                return f"{other.first_name} {other.last_name}".strip() or other.email.split("@")[0]
        return "Direct Message"

    def get_display_avatar(self, obj):
        if obj.room_type == "direct":
            request = self.context.get("request")
            if request and request.user:
                other = obj.participants.exclude(id=request.user.id).first()
                if other and hasattr(other, "avatar") and other.avatar:
                    return request.build_absolute_uri(other.avatar.url) if request else other.avatar.url
        return None
    
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "name", "avatar"]

    def get_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip()
        return name if name else obj.email.split("@")[0]

    def get_avatar(self, obj):
        if hasattr(obj, "avatar") and obj.avatar:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return None


class ReplySnippetSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "sender_name", "content", "image"]

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}".strip() or obj.sender.email.split("@")[0]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)
    reply_to = ReplySnippetSerializer(read_only=True)
    reply_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "room", "sender", "reply_to", "reply_to_id", "content", "image", "image_url", "is_read", "created_at"]
        read_only_fields = ["id", "sender", "created_at"]

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def create(self, validated_data):
        reply_to_id = validated_data.pop("reply_to_id", None)
        if reply_to_id:
            validated_data["reply_to"] = Message.objects.filter(id=reply_to_id).first()
        return super().create(validated_data)