from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import FamilyMembership, RoleChoices


class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    family_name = serializers.CharField(source="family.name", read_only=True)

    class Meta:
        model = FamilyMembership
        fields = [
            "id", "user", "user_email", "user_full_name",
            "family", "family_name", "role", "joined_at", "updated_at",
        ]
        read_only_fields = [
            "id", "user", "user_email", "user_full_name",
            "family", "family_name", "joined_at", "updated_at",
        ]


class RoleUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=RoleChoices.choices)

    def validate_role(self, value):
        if value == RoleChoices.OWNER:
            raise serializers.ValidationError(
                _("Ownership cannot be reassigned this way.")
            )
        return value