from django.urls import path
from .views import PostLikeView, PostLikesListView

urlpatterns = [
    path("posts/<int:id>/like/", PostLikeView.as_view(), name="post-like"),
    path("posts/<int:id>/likes/", PostLikesListView.as_view(), name="post-likes-list"),
]