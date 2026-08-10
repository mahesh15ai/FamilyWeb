from django.urls import path
from .views import VideoListCreateView, VideoDetailView

urlpatterns = [
    path("", VideoListCreateView.as_view(), name="video-list-create"),
    path("<int:id>/", VideoDetailView.as_view(), name="video-detail"),
]