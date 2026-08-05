from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import FamilyMembership, RoleChoices


def get_membership_for_user(*, user):
    return FamilyMembership.objects.filter(user=user).select_related("family").first()


def create_owner_membership(*, user, family) -> FamilyMembership:
    """
    Called automatically when a family is created.
    Gives the creator an OWNER membership right away.
    """
    return FamilyMembership.objects.create(user=user, family=family, role=RoleChoices.OWNER)


def create_member_membership(*, user, family) -> FamilyMembership:
    """
    Called when a join request is approved.
    Gives the joining user a plain MEMBER membership.
    """
    return FamilyMembership.objects.create(user=user, family=family, role=RoleChoices.MEMBER)


def list_family_members(*, family):
    return FamilyMembership.objects.filter(family=family).select_related("user")


def _get_actor_membership_or_raise(*, actor, family):
    membership = FamilyMembership.objects.filter(user=actor, family=family).first()
    allowed_roles = [RoleChoices.OWNER, getattr(RoleChoices, "SUPER_ADMIN", "SUPER_ADMIN")]
    
    if not membership or membership.role not in allowed_roles:
        if getattr(actor, "role", "") != "admin":
            raise PermissionDenied(_("Only the owner or a super admin can perform this action."))
            
    return membership


def require_admin_membership(*, actor, family) -> FamilyMembership:
    """
    Public wrapper so other apps (e.g. joinrequests) can reuse the same
    owner/super-admin permission check without reaching into a private helper.
    """
    return _get_actor_membership_or_raise(actor=actor, family=family)


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


def search_family_members(*, actor, query: str):
    """
    Searches by first name, last name, or email — scoped strictly to
    the actor's own family, so no one can search across families
    they don't belong to.
    """
    membership = get_membership_for_user(user=actor)
    if not membership:
        return FamilyMembership.objects.none()

    base_qs = FamilyMembership.objects.filter(family=membership.family).select_related("user")

    query = (query or "").strip()
    if not query:
        return base_qs

    return base_qs.filter(
        Q(user__first_name__icontains=query)
        | Q(user__last_name__icontains=query)
        | Q(user__email__icontains=query)
    )