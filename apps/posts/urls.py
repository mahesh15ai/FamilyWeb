from django.urls import path
from .views import MyPostsAPIView, PostDetailAPIView, PostListCreateAPIView

app_name = "posts"

urlpatterns = [
    path("", PostListCreateAPIView.as_view(), name="post-list-create"),
    path("my-posts/", MyPostsAPIView.as_view(), name="my-posts"),
    path("<int:pk>/", PostDetailAPIView.as_view(), name="post-detail"),
]