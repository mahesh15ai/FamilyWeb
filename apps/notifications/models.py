from django.db import models
from django.conf import settings
from apps.families.models import Family


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('new_post', 'New Post'),
        ('new_comment', 'New Comment'),
        ('new_event', 'New Event'),
        ('join_request', 'Join Request'),
        ('request_accepted', 'Request Accepted'),
        ('birthday', 'Birthday Alert'),
        ('general', 'General Announcement'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='triggered_notifications',
        null=True,
        blank=True
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default='general'
    )
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, default='')
    target_url = models.CharField(max_length=255, blank=True, default='/dashboard')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.recipient.email} - {self.title} ({'Read' if self.is_read else 'Unread'})"