from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class JoinRequestStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    APPROVED = "APPROVED", _("Approved")
    REJECTED = "REJECTED", _("Rejected")


class JoinRequest(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="join_requests",
    )
    family = models.ForeignKey(
        "families.Family",
        on_delete=models.CASCADE,
        related_name="join_requests",
    )
    status = models.CharField(
        max_length=20, choices=JoinRequestStatus.choices, default=JoinRequestStatus.PENDING
    )

    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_join_requests",
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "join_requests"
        verbose_name = _("join request")
        verbose_name_plural = _("join requests")
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["family", "status"]),
            models.Index(fields=["user"]),
        ]
        constraints = [
            # A user can only have one PENDING request outstanding at a time
            # (mirrors the one-membership-per-user rule from FamilyMembership).
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(status=JoinRequestStatus.PENDING),
                name="unique_pending_join_request_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.family.name} ({self.status})"