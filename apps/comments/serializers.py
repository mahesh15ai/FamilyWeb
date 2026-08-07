from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.id")
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "author_name", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "author_name", "created_at", "updated_at"]

    def get_author_name(self, obj):
        if not obj.author:
            return "Member"
        return getattr(obj.author, "full_name", None) or getattr(obj.author, "username", None) or getattr(obj.author, "email", "Member")


class CommentCreateSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "content", "author_name", "created_at"]
        read_only_fields = ["id", "author_name", "created_at"]

    def get_author_name(self, obj):
        if not obj.author:
            return "Member"
        return getattr(obj.author, "full_name", None) or getattr(obj.author, "username", None) or getattr(obj.author, "email", "Member")

    def validate_content(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Comment content cannot be blank.")
        if len(trimmed) > 150:
            raise serializers.ValidationError("Comment cannot exceed 150 characters.")
        return trimmed


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "content", "updated_at"]
        read_only_fields = ["id", "updated_at"]

    def validate_content(self, value):
        trimmed = value.strip()
        if not trimmed:
            raise serializers.ValidationError("Comment content cannot be blank.")
        if len(trimmed) > 150:
            raise serializers.ValidationError("Comment cannot exceed 150 characters.")
        return trimmed