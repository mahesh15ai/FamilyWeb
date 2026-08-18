from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()


def create_notification(recipient, title, message="", actor=None, family=None, notification_type="general", target_url="/dashboard"):
    """
    Helper function to dispatch a notification to a specific user.
    Prevents self-notification.
    """
    if actor and recipient and recipient.id == actor.id:
        return None

    if not recipient:
        return None

    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        family=family,
        notification_type=notification_type,
        title=title,
        message=message,
        target_url=target_url,
    )


def notify_family_members(family, title, message="", actor=None, notification_type="general", target_url="/dashboard", exclude_users=None):
    """
    Dispatches notifications to all active user members of a family workspace.
    Handles both direct User relations and FamilyMembership models.
    """
    if not family:
        return []

    excluded_ids = set()
    if actor:
        excluded_ids.add(actor.id)
    if exclude_users:
        excluded_ids.update(u.id for u in exclude_users)

    # Resolve actual User instances from family memberships
    recipient_users = []
    
    if hasattr(family, 'members'):
        # Check if members returns FamilyMembership objects or User objects
        members_query = family.members.all()
        for item in members_query:
            # If item is a FamilyMembership, extract the user
            user_obj = getattr(item, 'user', item)
            if isinstance(user_obj, User) and user_obj.id not in excluded_ids:
                recipient_users.append(user_obj)
    elif hasattr(family, 'memberships'):
        for membership in family.memberships.select_related('user').all():
            if membership.user and membership.user.id not in excluded_ids:
                recipient_users.append(membership.user)

    # Deduplicate users
    unique_recipients = {u.id: u for u in recipient_users}.values()

    notifications = [
        Notification(
            recipient=user,
            actor=actor,
            family=family,
            notification_type=notification_type,
            title=title,
            message=message,
            target_url=target_url,
        )
        for user in unique_recipients
    ]
    
    return Notification.objects.bulk_create(notifications)