from django.urls import path
from .views import (
    CommentDetailAPIView,
    CommentListCreateAPIView,
    PostCommentsListAPIView,
)

urlpatterns = [
    path("", CommentListCreateAPIView.as_view(), name="comment-create"),
    path("<int:pk>/", CommentDetailAPIView.as_view(), name="comment-detail"),
    path("post/<int:post_id>/", PostCommentsListAPIView.as_view(), name="post-comments"),
]