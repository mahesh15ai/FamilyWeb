from django.db.models.signals import post_save
from django.dispatch import receiver
from .services import notify_family_members, create_notification


@receiver(post_save, sender='posts.Post')
def notify_on_new_post(sender, instance, created, **kwargs):
    """
    Notify all family members when a new post is published.
    """
    if created and instance.family:
        actor = getattr(instance, 'author', None) or getattr(instance, 'user', None) or getattr(instance, 'created_by', None)
        if not actor:
            return

        author_name = f"{actor.first_name} {actor.last_name}".strip() or actor.email.split('@')[0]
        content_text = getattr(instance, 'content', '') or getattr(instance, 'caption', '') or ''
        preview = (content_text[:60] + '...') if len(content_text) > 60 else content_text

        notify_family_members(
            family=instance.family,
            title=f"New post from {author_name}",
            message=preview,
            actor=actor,
            notification_type="new_post",
            target_url="/posts",
        )


@receiver(post_save, sender='comments.Comment')
def notify_on_new_comment(sender, instance, created, **kwargs):
    """
    Notify the post author when someone comments on their post.
    """
    if created and instance.post:
        actor = getattr(instance, 'author', None) or getattr(instance, 'user', None)
        post_author = getattr(instance.post, 'author', None) or getattr(instance.post, 'user', None)

        if actor and post_author and post_author != actor:
            author_name = f"{actor.first_name} {actor.last_name}".strip() or actor.email.split('@')[0]
            comment_text = getattr(instance, 'content', '') or getattr(instance, 'text', '') or ''
            preview = (comment_text[:50] + '...') if len(comment_text) > 50 else comment_text

            create_notification(
                recipient=post_author,
                actor=actor,
                family=getattr(instance.post, 'family', None),
                notification_type="new_comment",
                title=f"{author_name} commented on your post",
                message=preview,
                target_url="/posts",
            )


@receiver(post_save, sender='events.Event')
def notify_on_new_event(sender, instance, created, **kwargs):
    """
    Notify all family members when a new event is scheduled.
    """
    if created and instance.family:
        actor = getattr(instance, 'created_by', None) or getattr(instance, 'user', None)
        if not actor:
            return

        creator_name = f"{actor.first_name} {actor.last_name}".strip() or actor.email.split('@')[0]
        date_str = str(getattr(instance, 'start_date', ''))

        notify_family_members(
            family=instance.family,
            title=f"New Event: {instance.title}",
            message=f"{creator_name} added an event for {date_str}",
            actor=actor,
            notification_type="new_event",
            target_url="/events",
        )


@receiver(post_save, sender='joinrequests.JoinRequest')
def notify_on_join_request(sender, instance, created, **kwargs):
    """
    Notify the family owner/admins when someone requests to join.
    """
    if created and instance.family and instance.user:
        family = instance.family
        requester_name = f"{instance.user.first_name} {instance.user.last_name}".strip() or instance.user.email.split('@')[0]

        recipient = (
            getattr(family, 'created_by', None)
            or getattr(family, 'owner', None)
            or getattr(family, 'admin', None)
        )
        if recipient and recipient != instance.user:
            create_notification(
                recipient=recipient,
                actor=instance.user,
                family=family,
                notification_type="join_request",
                title="New Join Request",
                message=f"{requester_name} has requested to join {family.name}",
                target_url="/families/join-requests",
            )