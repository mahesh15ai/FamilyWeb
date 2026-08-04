from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.membership.models import FamilyMembership
from apps.membership.services import get_membership_for_user

from .models import Relationship, RelationshipType

MAX_PARENTS_PER_MEMBER = 2


def _require_same_family(*, actor, from_member: FamilyMembership, to_member: FamilyMembership) -> None:
    """
    The two members must belong to the same family, and the person
    making the change must themself be a member of that same family —
    stops anyone from wiring up relationships in a family they're not
    even part of.
    """
    if from_member.family_id != to_member.family_id:
        raise ValidationError({"detail": _("Both members must belong to the same family.")})

    actor_membership = get_membership_for_user(user=actor)
    if not actor_membership or actor_membership.family_id != from_member.family_id:
        raise PermissionDenied(_("You can only manage relationships within your own family."))


def create_relationship(*, actor, from_member_id: int, to_member_id: int, relationship_type: str) -> Relationship:
    from_member = FamilyMembership.objects.select_related("family").get(pk=from_member_id)
    to_member = FamilyMembership.objects.select_related("family").get(pk=to_member_id)

    _require_same_family(actor=actor, from_member=from_member, to_member=to_member)

    if from_member_id == to_member_id:
        raise ValidationError({"detail": _("A member cannot have a relationship with themself.")})

    if relationship_type == RelationshipType.PARENT:
        if Relationship.objects.filter(
            from_member=to_member, to_member=from_member, relationship_type=RelationshipType.PARENT
        ).exists():
            raise ValidationError(
                {"detail": _("This would create a contradiction — that member is already recorded as this member's parent.")}
            )

        existing_parent_count = Relationship.objects.filter(
            to_member=to_member, relationship_type=RelationshipType.PARENT
        ).count()
        if existing_parent_count >= MAX_PARENTS_PER_MEMBER:
            raise ValidationError({"detail": _("This member already has the maximum number of recorded parents.")})

    if relationship_type in (RelationshipType.SPOUSE, RelationshipType.SIBLING):
        if Relationship.objects.filter(
            from_member=to_member, to_member=from_member, relationship_type=relationship_type
        ).exists():
            raise ValidationError({"detail": _("This relationship has already been recorded.")})

    if Relationship.objects.filter(
        from_member=from_member, to_member=to_member, relationship_type=relationship_type
    ).exists():
        raise ValidationError({"detail": _("This relationship has already been recorded.")})

    return Relationship.objects.create(
        from_member=from_member,
        to_member=to_member,
        relationship_type=relationship_type,
        created_by=actor,
    )


def update_relationship(*, actor, relationship: Relationship, relationship_type: str) -> Relationship:
    _require_same_family(actor=actor, from_member=relationship.from_member, to_member=relationship.to_member)
    relationship.relationship_type = relationship_type
    relationship.full_clean()
    relationship.save(update_fields=["relationship_type", "updated_at"])
    return relationship


def delete_relationship(*, actor, relationship: Relationship) -> None:
    _require_same_family(actor=actor, from_member=relationship.from_member, to_member=relationship.to_member)
    relationship.delete()


def list_family_relationships(*, actor):
    membership = get_membership_for_user(user=actor)
    if not membership:
        return Relationship.objects.none()
    return Relationship.objects.filter(from_member__family=membership.family).select_related(
        "from_member__user", "to_member__user"
    )


def build_family_tree_graph(*, actor) -> dict:
    """
    Returns {nodes, edges} for the whole family — every member as a
    node, every relationship as an edge. PARENT edges are mirrored
    into an extra CHILD edge (the inverse direction) purely for
    rendering convenience — CHILD is never stored, only computed here.
    """
    membership = get_membership_for_user(user=actor)
    if not membership:
        return {"nodes": [], "edges": []}

    members = FamilyMembership.objects.filter(family=membership.family).select_related("user")
    relationships = Relationship.objects.filter(from_member__family=membership.family).select_related(
        "from_member", "to_member"
    )

    nodes = [
        {
            "id": m.id,
            "user_id": m.user_id,
            "name": m.user.full_name or m.user.email,
            "role": m.role,
            "profile_photo": m.user.profile_photo.url if m.user.profile_photo else None,
        }
        for m in members
    ]

    edges = []
    for rel in relationships:
        edges.append({"from_id": rel.from_member_id, "to_id": rel.to_member_id, "type": rel.relationship_type})
        if rel.relationship_type == RelationshipType.PARENT:
            edges.append({"from_id": rel.to_member_id, "to_id": rel.from_member_id, "type": "CHILD"})

    return {"nodes": nodes, "edges": edges}