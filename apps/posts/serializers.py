from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()


class MentionUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name"]

    def get_full_name(self, obj):
        if hasattr(obj, "get_full_name") and obj.get_full_name():
            return obj.get_full_name()
        if obj.first_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.email.split("@")[0]


class PostCreateSerializer(serializers.ModelSerializer):
    mentioned_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Post
        fields = ["content", "image", "video", "mentioned_user_ids"]

    def validate(self, attrs):
        content = attrs.get("content", "").strip() if attrs.get("content") else ""
        image = attrs.get("image")
        video = attrs.get("video")

        if not content and not image and not video:
            raise serializers.ValidationError("Post must contain text, an image, or a video.")
        return attrs


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_profile_photo = serializers.SerializerMethodField()
    mentions = MentionUserSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "family",
            "author",
            "author_name",
            "author_profile_photo",
            "content",
            "image",
            "video",
            "mentions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_author_profile_photo(self, obj):
        if getattr(obj.author, "profile_photo", None):
            return obj.author.profile_photo.url
        return None


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["content", "image", "video"]