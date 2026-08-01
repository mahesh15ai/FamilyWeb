from django.urls import path

from .views import (
    FamilyDetailAPIView,
    FamilyListCreateAPIView,
    MyFamilyAPIView,
)

app_name = "families"

urlpatterns = [
    path("", FamilyListCreateAPIView.as_view(), name="family-list-create"),
    path("my-family/", MyFamilyAPIView.as_view(), name="my-family"),
    path("<int:pk>/", FamilyDetailAPIView.as_view(), name="family-detail"),
]