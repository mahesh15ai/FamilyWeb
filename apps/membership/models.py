from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class RoleChoices(models.TextChoices):
    OWNER = "OWNER", _("Owner")
    SUPER_ADMIN = "SUPER_ADMIN", _("Super Admin")
    MEMBER = "MEMBER", _("Member")


class FamilyMembership(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_membership",
    )
    family = models.ForeignKey(
        "families.Family",
        on_delete=models.CASCADE,
        related_name="members",
    )
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.MEMBER)

    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "family_memberships"
        verbose_name = _("family membership")
        verbose_name_plural = _("family memberships")
        ordering = ["-joined_at"]
        indexes = [
            models.Index(fields=["family"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.family.name} ({self.role})"