from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.families.models import Family
from .models import Album
from .serializers import AlbumSerializer


def get_user_family(user):
    """
    Finds the family the user belongs to, whether they are
    the owner or a registered member.
    """
    # 1. Family created/owned by user
    family = Family.objects.filter(created_by=user).first()
    if family:
        return family

    # 2. Check if user belongs to a family via Membership relation
    if hasattr(user, "memberships"):
        membership = user.memberships.select_related("family").first()
        if membership:
            return membership.family

    # 3. Direct family query fallback
    return Family.objects.filter(members__user=user).first()


class AlbumListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # GET /api/albums/ -> Returns ALL albums belonging to the family
    def get(self, request):
        family = get_user_family(request.user)

        if not family:
            return Response(
                {"count": 0, "results": []},
                status=status.HTTP_200_OK,
            )

        # Query by family ID so ALL family members see ALL albums created in this family
        albums = Album.objects.filter(family=family)
        serializer = AlbumSerializer(albums, many=True)

        return Response(
            {
                "count": albums.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # POST /api/albums/ -> Any authenticated family member can create an album
    def post(self, request):
        title = request.data.get("title")
        if not title:
            return Response(
                {"detail": "Title is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        family = get_user_family(request.user)

        if not family:
            return Response(
                {"detail": "You must belong to an active family to create an album."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Attach the user's active family to the album
        album = Album.objects.create(
            title=title,
            description=request.data.get("description", ""),
            family=family,
            created_by=request.user,
        )

        serializer = AlbumSerializer(album)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AlbumDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        return get_object_or_404(Album, id=id)

    # GET /api/albums/{id}/
    def get(self, request, id):
        album = self.get_object(id)
        serializer = AlbumSerializer(album)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PATCH /api/albums/{id}/
    def patch(self, request, id):
        album = self.get_object(id)

        if "title" in request.data:
            album.title = request.data["title"]
        if "description" in request.data:
            album.description = request.data["description"]

        album.save()
        serializer = AlbumSerializer(album)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE /api/albums/{id}/
    def delete(self, request, id):
        album = self.get_object(id)
        album.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)