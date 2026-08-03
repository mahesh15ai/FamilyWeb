from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.families.models import Family
from apps.membership.services import create_member_membership, get_membership_for_user, require_admin_membership

from .models import JoinRequest, JoinRequestStatus


def create_join_request(*, user, family_code: str) -> JoinRequest:
    """
    Submits a request to join a family by its invite code.
    A user who already belongs to a family (owner or member) can't request
    to join another one — mirrors the one-membership-per-user rule.
    """
    family_code = family_code.strip().upper()
    family = Family.objects.filter(family_code=family_code).first()
    if not family:
        raise ValidationError({"family_code": _("No family found with this invite code.")})

    if get_membership_for_user(user=user):
        raise ValidationError(
            {"detail": _("You already belong to a family. Leave it before requesting to join another.")}
        )

    if JoinRequest.objects.filter(user=user, status=JoinRequestStatus.PENDING).exists():
        raise ValidationError(
            {"detail": _("You already have a pending join request. Withdraw it before submitting a new one.")}
        )

    try:
        return JoinRequest.objects.create(user=user, family=family)
    except IntegrityError as exc:
        raise ValidationError(
            {"detail": _("You already have a pending join request.")}
        ) from exc


def list_join_requests_for_actor(*, actor):
    """
    Returns all join requests (pending and past) for the actor's own family.
    Only the owner or a super admin may view them.
    """
    membership = get_membership_for_user(user=actor)
    if not membership:
        raise ValidationError({"detail": _("You are not part of any family yet.")})

    require_admin_membership(actor=actor, family=membership.family)
    return JoinRequest.objects.filter(family=membership.family)


def get_join_request_for_actor_or_raise(*, actor, join_request: JoinRequest) -> JoinRequest:
    """
    A join request is visible to the requester themself, or to an owner/super
    admin of the target family.
    """
    if join_request.user_id == actor.id:
        return join_request
    require_admin_membership(actor=actor, family=join_request.family)
    return join_request


@transaction.atomic
def approve_join_request(*, actor, join_request: JoinRequest) -> JoinRequest:
    require_admin_membership(actor=actor, family=join_request.family)

    if join_request.status != JoinRequestStatus.PENDING:
        raise ValidationError({"detail": _("This join request has already been decided.")})

    if get_membership_for_user(user=join_request.user):
        raise ValidationError({"detail": _("This user already belongs to a family.")})

    membership = create_member_membership(user=join_request.user, family=join_request.family)

    join_request.status = JoinRequestStatus.APPROVED
    join_request.decided_by = actor
    join_request.decided_at = timezone.now()
    join_request.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])

    # The user can only end up in one family — clean up any other requests
    # they may have pending elsewhere.
    JoinRequest.objects.filter(
        user=join_request.user, status=JoinRequestStatus.PENDING
    ).exclude(pk=join_request.pk).update(
        status=JoinRequestStatus.REJECTED, decided_by=actor, decided_at=timezone.now()
    )

    join_request._new_membership = membership  # noqa: SLF001 (convenience for the view/serializer)
    return join_request


def reject_join_request(*, actor, join_request: JoinRequest) -> JoinRequest:
    require_admin_membership(actor=actor, family=join_request.family)

    if join_request.status != JoinRequestStatus.PENDING:
        raise ValidationError({"detail": _("This join request has already been decided.")})

    join_request.status = JoinRequestStatus.REJECTED
    join_request.decided_by = actor
    join_request.decided_at = timezone.now()
    join_request.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])
    return join_request


def withdraw_or_delete_join_request(*, actor, join_request: JoinRequest) -> None:
    """
    The requester can withdraw their own request; an owner/super admin of the
    target family can also remove it (e.g. to clear stale history).
    """
    is_requester = join_request.user_id == actor.id
    if not is_requester:
        require_admin_membership(actor=actor, family=join_request.family)

    join_request.delete()