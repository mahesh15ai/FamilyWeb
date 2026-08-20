import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from apps.notifications.models import Notification
from apps.membership.models import FamilyMembership

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Message)
def create_chat_message_notification(sender, instance, created, **kwargs):
    if not created:
        return

    room = instance.room
    sender_user = instance.sender
    sender_name = (
        f"{sender_user.first_name} {sender_user.last_name}".strip()
        or sender_user.email.split("@")[0]
    )
    preview = instance.content if instance.content else "Sent a photo 📷"

    try:
        # Case A: Group Lounge Room -> Notify all other family members
        if room.room_type == "group":
            memberships = (
                FamilyMembership.objects.filter(family=room.family)
                .exclude(user=sender_user)
                .select_related("user")
            )

            notifications = [
                Notification(
                    recipient=m.user,
                    sender=sender_user,
                    notification_type="new_message",
                    title=room.name or "Family Lounge",
                    message=f"{sender_name}: {preview[:60]}",
                    target_url="/chat",
                )
                for m in memberships
            ]
            if notifications:
                Notification.objects.bulk_create(notifications)

        # Case B: 1-on-1 Direct Message -> Notify the other participant
        elif room.room_type == "direct":
            recipient = room.participants.exclude(id=sender_user.id).first()
            if recipient:
                Notification.objects.create(
                    recipient=recipient,
                    sender=sender_user,
                    notification_type="new_message",
                    title=f"Message from {sender_name}",
                    message=preview[:60],
                    target_url="/chat",
                )
    except Exception as e:
        logger.error(f"Failed to create chat notification: {e}")