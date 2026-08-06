from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.membership.services import get_membership_for_user

from .models import Post

User = get_user_model()


def _extract_and_set_mentions(post: Post, content: str, explicit_user_ids: list[int] | None = None) -> None:
    """
    Parses the post text content to ensure ONLY users whose names match an '@' tag
    in the text get added to post.mentions.
    """
    if not content or "@" not in content:
        post.mentions.clear()
        return

    # Parse explicitly passed IDs if provided
    valid_ids = set()
    if explicit_user_ids:
        if isinstance(explicit_user_ids, str):
            explicit_user_ids = [int(x) for x in explicit_user_ids.split(",") if str(x).isdigit()]
        
        # Filter explicitly passed IDs against DB users
        candidate_users = User.objects.filter(id__in=explicit_user_ids)
        for user in candidate_users:
            full_name = getattr(user, "full_name", None) or f"{user.first_name} {user.last_name}".strip() or user.first_name
            if full_name and f"@{full_name}".lower() in content.lower():
                valid_ids.add(user.id)

    # Fallback auto-detection by name match if explicit IDs were empty or incomplete
    if not valid_ids:
        content_lower = content.lower()
        all_users = User.objects.all()
        for user in all_users:
            display_name = (
                getattr(user, "full_name", None)
                or f"{user.first_name} {user.last_name}".strip()
                or user.first_name
                or user.email.split("@")[0]
            )
            if display_name and f"@{display_name}".lower() in content_lower:
                valid_ids.add(user.id)

    post.mentions.set(list(valid_ids))


def create_post(
    *,
    user,
    content: str = "",
    image=None,
    video=None,
    mentioned_user_ids: list[int] | None = None,
) -> Post:
    membership = get_membership_for_user(user=user)
    if not membership:
        raise ValidationError({"detail": _("You must be part of a family to post.")})

    with transaction.atomic():
        post = Post.objects.create(
            family=membership.family,
            author=user,
            content=content,
            image=image,
            video=video,
        )

        _extract_and_set_mentions(post, content, mentioned_user_ids)

    return post


def list_family_posts(*, user):
    membership = get_membership_for_user(user=user)
    if not membership:
        return Post.objects.none()

    return (
        Post.objects.filter(family=membership.family)
        .select_related("author")
        .prefetch_related("mentions")
    )


def list_my_posts(*, user):
    return (
        Post.objects.filter(author=user)
        .select_related("author")
        .prefetch_related("mentions")
    )


def update_post(
    *,
    user,
    post: Post,
    content: str = "",
    image=None,
    video=None,
    mentioned_user_ids: list[int] | None = None,
) -> Post:
    if post.author_id != user.id:
        raise PermissionDenied(_("You can only edit your own posts."))

    with transaction.atomic():
        post.content = content
        if image is not None:
            post.image = image
        if video is not None:
            post.video = video

        _extract_and_set_mentions(post, content, mentioned_user_ids)

        post.full_clean()
        post.save()

    return post


def delete_post(*, user, post: Post) -> None:
    membership = get_membership_for_user(user=user)
    is_admin_or_owner = membership and membership.role in [
        "OWNER",
        "SUPER_ADMIN",
        "ADMIN",
    ]

    if post.author_id != user.id and not is_admin_or_owner:
        raise PermissionDenied(_("You can only delete your own posts."))

    post.delete()