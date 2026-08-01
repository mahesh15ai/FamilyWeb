from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.membership.services import create_owner_membership

from .models import Family


def create_family(*, user, validated_data: dict) -> Family:
    """
    Creates a new family. created_by is always the logged-in user —
    never taken from the request body. A user may create at most one family.
    """
    if Family.objects.filter(created_by=user).exists():
        raise ValidationError(
            {"detail": _("You have already created a family. Each user can create only one.")}
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
    return Family.objects.filter(created_by=user).first()