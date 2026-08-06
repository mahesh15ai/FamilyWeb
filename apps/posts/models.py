from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)

    family = models.ForeignKey(
        "families.Family",
        on_delete=models.CASCADE,
        related_name="posts",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    content = models.TextField(max_length=2000, blank=True, default="")

    # Media attachment fields
    image = models.ImageField(upload_to="posts/images/", blank=True, null=True)
    video = models.FileField(upload_to="posts/videos/", blank=True, null=True)

    # Member mentions
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="mentioned_in_posts",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "posts"
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["family", "-created_at"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        preview = self.content[:40] if self.content else "Media Post"
        return f"{self.author.email}: {preview}"