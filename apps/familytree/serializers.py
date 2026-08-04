from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.membership.models import FamilyMembership

from .models import Relationship, RelationshipType


class RelationshipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = ["from_member", "to_member", "relationship_type"]

    def validate(self, attrs):
        if attrs["from_member"] == attrs["to_member"]:
            raise serializers.ValidationError(_("A member cannot have a relationship with themself."))
        return attrs


class RelationshipSerializer(serializers.ModelSerializer):
    from_member_name = serializers.CharField(source="from_member.user.full_name", read_only=True)
    to_member_name = serializers.CharField(source="to_member.user.full_name", read_only=True)

    class Meta:
        model = Relationship
        fields = [
            "id", "from_member", "from_member_name", "to_member", "to_member_name",
            "relationship_type", "created_by", "created_at", "updated_at",
        ]
        read_only_fields = fields


class RelationshipUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = ["relationship_type"]


class FamilyTreeNodeSerializer(serializers.Serializer):
    """A single person in the graph — one FamilyMembership."""

    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    role = serializers.CharField()
    profile_photo = serializers.CharField(allow_null=True)


class FamilyTreeEdgeSerializer(serializers.Serializer):
    """A single relationship line in the graph."""

    from_id = serializers.IntegerField()
    to_id = serializers.IntegerField()
    type = serializers.ChoiceField(choices=RelationshipType.choices + [("CHILD", "Child")])