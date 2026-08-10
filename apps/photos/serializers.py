from rest_framework import serializers
from .models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source="uploaded_by.username")
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            "id",
            "album",
            "image",
            "image_url",
            "caption",
            "uploaded_by",
            "uploaded_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "uploaded_by", "created_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None