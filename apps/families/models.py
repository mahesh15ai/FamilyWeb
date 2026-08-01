import uuid

from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


def family_logo_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"family_logos/{instance.uuid}.{ext}"


def family_cover_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"family_covers/{instance.uuid}.{ext}"


def generate_family_code():
    """Generates a short, human-shareable, unique-ish invite code (e.g. 8F3K9X2Q)."""
    return get_random_string(8, allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789")


class Family(models.Model):
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    name = models.CharField(_("family name"), max_length=150)
    family_code = models.CharField(
        max_length=10, unique=True, default=generate_family_code, db_index=True
    )

    logo = models.ImageField(upload_to=family_logo_path, null=True, blank=True)
    cover_image = models.ImageField(upload_to=family_cover_path, null=True, blank=True)
    description = models.TextField(max_length=500, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_families",
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "families"
        verbose_name = _("family")
        verbose_name_plural = _("families")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["family_code"]),
            models.Index(fields=["uuid"]),
        ]

    def __str__(self):
        return self.name