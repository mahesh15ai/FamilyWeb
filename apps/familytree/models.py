from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _


class RelationshipType(models.TextChoices):
    """
    Only direct, storable relationships. CHILD is intentionally NOT a
    stored type — it's always the inverse of PARENT and is computed
    on read (in the graph endpoint), so a parent/child pair can never
    end up stored inconsistently as two contradicting rows.
    """

    PARENT = "PARENT", _("Parent")   # from_member is the parent of to_member
    SPOUSE = "SPOUSE", _("Spouse")   # symmetric
    SIBLING = "SIBLING", _("Sibling")  # symmetric


class Relationship(models.Model):
    id = models.BigAutoField(primary_key=True)

    from_member = models.ForeignKey(
        "membership.FamilyMembership",
        on_delete=models.CASCADE,
        related_name="relationships_from",
    )
    to_member = models.ForeignKey(
        "membership.FamilyMembership",
        on_delete=models.CASCADE,
        related_name="relationships_to",
    )
    relationship_type = models.CharField(max_length=20, choices=RelationshipType.choices)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_relationships",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "family_tree_relationships"
        verbose_name = _("relationship")
        verbose_name_plural = _("relationships")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["from_member"]),
            models.Index(fields=["to_member"]),
            models.Index(fields=["relationship_type"]),
        ]
        constraints = [
            # A member can't be related to themself.
            models.CheckConstraint(
                condition=~Q(from_member=F("to_member")),
                name="relationship_cannot_self_reference",
            ),
            # The exact same (from, to, type) combination can't be recorded twice.
            models.UniqueConstraint(
                fields=["from_member", "to_member", "relationship_type"],
                name="unique_relationship_pair_per_type",
            ),
        ]

    def __str__(self):
        return f"{self.from_member_id} --{self.relationship_type}--> {self.to_member_id}"