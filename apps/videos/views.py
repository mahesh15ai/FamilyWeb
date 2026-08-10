from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.albums.models import Album
from .models import Video
from .serializers import VideoSerializer


class VideoListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # GET /api/videos/?album={album_id}
    def get(self, request):
        album_id = request.query_params.get("album")
        if album_id:
            videos = Video.objects.filter(album_id=album_id)
        else:
            videos = Video.objects.all()

        serializer = VideoSerializer(videos, many=True, context={"request": request})
        return Response(
            {
                "count": videos.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # POST /api/videos/ -> Handles single or multiple video uploads
    def post(self, request):
        album_id = request.data.get("album")
        if not album_id:
            return Response(
                {"detail": "album (ID) is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        album = get_object_or_404(Album, id=album_id)

        videos_list = request.FILES.getlist("videos")
        if not videos_list and "video" in request.FILES:
            videos_list = [request.FILES["video"]]

        if not videos_list:
            return Response(
                {"detail": "At least one video file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        title = request.data.get("title", "")
        caption = request.data.get("caption", "")
        created_videos = []

        for vid in videos_list:
            video_obj = Video.objects.create(
                album=album,
                video_file=vid,
                title=title or vid.name,
                caption=caption,
                uploaded_by=request.user,
            )
            created_videos.append(video_obj)

        serializer = VideoSerializer(
            created_videos, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VideoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        return get_object_or_404(Video, id=id)

    # GET /api/videos/{id}/
    def get(self, request, id):
        video = self.get_object(id)
        serializer = VideoSerializer(video, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE /api/videos/{id}/
    def delete(self, request, id):
        video = self.get_object(id)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)