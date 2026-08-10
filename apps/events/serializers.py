from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Event
        fields = [
            "id",
            "family",
            "title",
            "description",
            "start_date",
            "start_time",
            "location",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "family", "created_by", "created_at"]