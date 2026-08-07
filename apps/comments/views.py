from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Comment
from .permissions import IsCommentAuthorOrAdmin
from .serializers import (
    CommentCreateSerializer,
    CommentUpdateSerializer,
)


def get_author_display_name(user):
    if not user:
        return "Member"
    return getattr(user, "full_name", None) or getattr(user, "username", None) or getattr(user, "email", "Member")


def get_author_photo_url(user, request):
    if not user:
        return None
    # Adjust 'profile_photo' field name to match your custom User model field
    photo = getattr(user, "profile_photo", None) or getattr(user, "avatar", None)
    if photo and hasattr(photo, "url"):
        return request.build_absolute_uri(photo.url)
    return None


class CommentListCreateAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentCreateSerializer

    def post(self, request):
        """CREATE: Add a comment"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        comment = serializer.save(author=request.user)
        
        return Response(
            {
                "id": comment.id,
                "post": comment.post_id,
                "author": get_author_display_name(comment.author),
                "author_id": comment.author_id,
                "author_profile_photo": get_author_photo_url(comment.author, request),
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class CommentDetailAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCommentAuthorOrAdmin]
    queryset = Comment.objects.all()

    def patch(self, request, pk):
        """UPDATE: Edit a comment"""
        comment = self.get_object()
        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "id": comment.id,
                "content": comment.content,
                "updated_at": comment.updated_at.isoformat(),
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        """DELETE: Remove a comment"""
        comment = self.get_object()
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostCommentsListAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        """READ: List all comments on a post"""
        comments = Comment.objects.filter(post_id=post_id).select_related("author").order_by("created_at")
        
        results = [
            {
                "id": c.id,
                "post": c.post_id,
                "author": get_author_display_name(c.author),
                "author_id": c.author_id,
                "author_profile_photo": get_author_photo_url(c.author, request),
                "content": c.content,
                "created_at": c.created_at.isoformat() if hasattr(c, "created_at") and c.created_at else None,
            }
            for c in comments
        ]

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )