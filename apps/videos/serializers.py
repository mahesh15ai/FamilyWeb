from rest_framework import serializers
from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source="uploaded_by.username")
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "album",
            "video_file",
            "video_url",
            "title",
            "caption",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "uploaded_by", "created_at"]

    def get_video_url(self, obj):
        request = self.context.get("request")
        if obj.video_file and hasattr(obj.video_file, "url"):
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None