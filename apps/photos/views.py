from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.albums.models import Album
from .models import Photo
from .serializers import PhotoSerializer


class PhotoListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # GET /api/photos/?album={album_id}
    def get(self, request):
        album_id = request.query_params.get("album")
        if album_id:
            photos = Photo.objects.filter(album_id=album_id)
        else:
            photos = Photo.objects.all()

        serializer = PhotoSerializer(photos, many=True, context={"request": request})
        return Response(
            {
                "count": photos.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # POST /api/photos/ -> Handles single or multiple photo uploads
    def post(self, request):
        album_id = request.data.get("album")
        if not album_id:
            return Response(
                {"detail": "album (ID) is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        album = get_object_or_404(Album, id=album_id)

        # Retrieve images (supports multiple files under 'images' or single under 'image')
        images = request.FILES.getlist("images")
        if not images and "image" in request.FILES:
            images = [request.FILES["image"]]

        if not images:
            return Response(
                {"detail": "At least one image file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        caption = request.data.get("caption", "")
        created_photos = []

        for img in images:
            photo = Photo.objects.create(
                album=album,
                image=img,
                caption=caption,
                uploaded_by=request.user,
            )
            created_photos.append(photo)

        serializer = PhotoSerializer(
            created_photos, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PhotoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        return get_object_or_404(Photo, id=id)

    # GET /api/photos/{id}/
    def get(self, request, id):
        photo = self.get_object(id)
        serializer = PhotoSerializer(photo, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE /api/photos/{id}/
    def delete(self, request, id):
        photo = self.get_object(id)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)