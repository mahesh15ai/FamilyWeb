from rest_framework import serializers
from .models import Album


class AlbumSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.username")
    photo_count = serializers.SerializerMethodField()
    video_count = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = [
            "id",
            "title",
            "description",
            "family",
            "created_by",
            "created_by_name",
            "photo_count",
            "video_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "family", "created_by", "created_at", "updated_at"]

    def get_photo_count(self, obj):
        # Day 13 Photos module जोडल्यावर मोजले जाईल
        return getattr(obj, "photos", None).count() if hasattr(obj, "photos") else 0

    def get_video_count(self, obj):
        # Day 14 Videos module जोडल्यावर मोजले जाईल
        return getattr(obj, "videos", None).count() if hasattr(obj, "videos") else 0