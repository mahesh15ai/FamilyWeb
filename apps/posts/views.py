from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Post
from .serializers import PostCreateSerializer, PostSerializer, PostUpdateSerializer


@extend_schema(tags=["Posts"])
class PostListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(summary="List posts in my family", responses={200: PostSerializer(many=True)})
    def get(self, request):
        posts = services.list_family_posts(user=request.user)
        return Response(PostSerializer(posts, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Create a post", request=PostCreateSerializer, responses={201: PostSerializer})
    def post(self, request):
        serializer = PostCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = services.create_post(
            user=request.user,
            content=serializer.validated_data.get("content", ""),
            image=serializer.validated_data.get("image"),
            video=serializer.validated_data.get("video"),
            mentioned_user_ids=serializer.validated_data.get("mentioned_user_ids"),
        )
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Posts"])
class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return get_object_or_404(Post.objects.select_related("author").prefetch_related("mentions"), pk=pk)

    @extend_schema(summary="Get post details", responses={200: PostSerializer})
    def get(self, request, pk):
        post = self.get_object(pk)
        return Response(PostSerializer(post).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Update a post", request=PostUpdateSerializer, responses={200: PostSerializer})
    def patch(self, request, pk):
        post = self.get_object(pk)
        serializer = PostUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated = services.update_post(
            user=request.user,
            post=post,
            content=serializer.validated_data.get("content", post.content),
            image=serializer.validated_data.get("image"),
            video=serializer.validated_data.get("video"),
        )
        return Response(PostSerializer(updated).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Delete a post")
    def delete(self, request, pk):
        post = self.get_object(pk)
        services.delete_post(user=request.user, post=post)
        return Response({"message": _("Post deleted successfully.")}, status=status.HTTP_200_OK)


@extend_schema(tags=["Posts"])
class MyPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List my own posts", responses={200: PostSerializer(many=True)})
    def get(self, request):
        posts = services.list_my_posts(user=request.user)
        return Response(PostSerializer(posts, many=True).data, status=status.HTTP_200_OK)