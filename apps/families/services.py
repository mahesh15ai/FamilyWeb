from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.membership.services import create_owner_membership, get_membership_for_user

from .models import Family


def create_family(*, user, validated_data: dict) -> Family:
    """
    Creates a new family. created_by is always the logged-in user —
    never taken from the request body.

    A user may belong to only one family, whether as its owner or as a
    member of someone else's — so we check FamilyMembership (the real
    source of truth for "which family is this user in"), not just
    Family.created_by. This also blocks family creation for someone who
    already joined another family as a plain member.
    """
    if get_membership_for_user(user=user):
        raise ValidationError(
            {"detail": _("You're already part of a family. Leave your current family before creating a new one.")}
        )
    family = Family.objects.create(created_by=user, **validated_data)
    create_owner_membership(user=user, family=family)
    return family


def update_family(*, family: Family, user, validated_data: dict) -> Family:
    if family.created_by_id != user.id:
        raise PermissionDenied(_("Only the family owner can update this family."))

    for field, value in validated_data.items():
        setattr(family, field, value)
    family.full_clean(exclude=["family_code", "uuid"])
    family.save()
    return family


def delete_family(*, family: Family, user) -> None:
    if family.created_by_id != user.id:
        raise PermissionDenied(_("Only the family owner can delete this family."))
    family.delete()


def get_my_family(*, user) -> Family | None:
    """
    Returns the family the user belongs to — whether they created it
    (owner) or joined it as a member — via their FamilyMembership row,
    not just Family.created_by.
    """
    membership = get_membership_for_user(user=user)
    return membership.family if membership else None