from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import FamilyMembership, RoleChoices


def get_membership_for_user(*, user):
    return FamilyMembership.objects.filter(user=user).first()


def create_owner_membership(*, user, family) -> FamilyMembership:
    """
    Called automatically when a family is created.
    Gives the creator an OWNER membership right away.
    """
    return FamilyMembership.objects.create(user=user, family=family, role=RoleChoices.OWNER)


def list_family_members(*, family):
    return FamilyMembership.objects.filter(family=family)


def _get_actor_membership_or_raise(*, actor, family):
    membership = FamilyMembership.objects.filter(user=actor, family=family).first()
    if not membership or membership.role not in [RoleChoices.OWNER, RoleChoices.SUPER_ADMIN]:
        raise PermissionDenied(_("Only the owner or a super admin can perform this action."))
    return membership


def update_member_role(*, actor, membership: FamilyMembership, new_role: str) -> FamilyMembership:
    _get_actor_membership_or_raise(actor=actor, family=membership.family)

    if membership.role == RoleChoices.OWNER:
        raise ValidationError({"detail": _("The owner's role cannot be changed.")})

    membership.role = new_role
    membership.save(update_fields=["role", "updated_at"])
    return membership


def remove_member(*, actor, membership: FamilyMembership) -> None:
    _get_actor_membership_or_raise(actor=actor, family=membership.family)

    if membership.role == RoleChoices.OWNER:
        raise ValidationError({"detail": _("The owner cannot be removed from the family.")})

    membership.delete()