from rest_framework import serializers

from .models import JoinRequest


class JoinRequestCreateSerializer(serializers.Serializer):
    family_code = serializers.CharField(max_length=10)


class JoinRequestSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    family_name = serializers.CharField(source="family.name", read_only=True)
    decided_by_name = serializers.CharField(source="decided_by.full_name", read_only=True)

    class Meta:
        model = JoinRequest
        fields = [
            "id", "user", "user_email", "user_full_name",
            "family", "family_name", "status",
            "decided_by", "decided_by_name", "decided_at",
            "requested_at", "updated_at",
        ]
        read_only_fields = fields