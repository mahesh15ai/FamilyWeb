from django.urls import path
from .views import AlbumListCreateView, AlbumDetailView

urlpatterns = [
    path("", AlbumListCreateView.as_view(), name="album-list-create"),
    path("<int:id>/", AlbumDetailView.as_view(), name="album-detail"),
]