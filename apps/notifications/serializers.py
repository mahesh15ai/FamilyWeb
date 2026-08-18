from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    actor_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'target_url',
            'is_read',
            'created_at',
            'actor_name',
            'actor_avatar',
        ]

    def get_actor_name(self, obj):
        if not obj.actor:
            return "System"
        name = f"{obj.actor.first_name} {obj.actor.last_name}".strip()
        return name if name else obj.actor.email.split('@')[0]

    def get_actor_avatar(self, obj):
        if obj.actor and hasattr(obj.actor, 'avatar') and obj.actor.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.actor.avatar.url)
            return obj.actor.avatar.url
        return None