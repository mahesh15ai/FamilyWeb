from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Family


class FamilyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ["name", "description", "logo", "cover_image"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(_("Family name must be at least 2 characters."))
        return value


class FamilySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = Family
        fields = [
            "id", "uuid", "name", "family_code", "logo", "cover_image",
            "description", "created_by", "created_by_name", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "uuid", "family_code", "created_by", "created_by_name",
            "is_active", "created_at", "updated_at",
        ]


class FamilyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = ["name", "description", "logo", "cover_image"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(_("Family name must be at least 2 characters."))
        return value