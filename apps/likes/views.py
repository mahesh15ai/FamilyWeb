from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from apps.posts.models import Post
from .models import Like


class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # POST /api/posts/{id}/like/ -> Likes a post
    def post(self, request, id):
        post = get_object_or_404(Post, id=id)
        like, created = Like.objects.get_or_create(post=post, user=request.user)

        # Returns 201 Created if new like, or 200 OK if already liked
        return Response(
            {
                "post": post.id,
                "user": request.user.id,
                "liked_at": like.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    # DELETE /api/posts/{id}/like/ -> Removes the user's like
    def delete(self, request, id):
        post = get_object_or_404(Post, id=id)
        like = Like.objects.filter(post=post, user=request.user).first()

        if like:
            like.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PostLikesListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # GET /api/posts/{id}/likes/ -> Lists users who liked the post
    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        likes = Like.objects.filter(post=post).select_related("user")

        results = [
            {
                "user_id": like.user.id,
                "user": like.user.first_name or like.user.username,
            }
            for like in likes
        ]

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )