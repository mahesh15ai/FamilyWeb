from django.db import models
from django.conf import settings
from apps.albums.models import Album


class Video(models.Model):
    album = models.ForeignKey(
        Album, on_delete=models.CASCADE, related_name="videos"
    )
    video_file = models.FileField(upload_to="videos/%Y/%m/")
    title = models.CharField(max_length=255, blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="uploaded_videos"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Video {self.id} in Album {self.album.title}"