from django.urls import path

from .views import (
    FamilyTreeGraphAPIView,
    RelationshipDetailAPIView,
    RelationshipListCreateAPIView,
)

app_name = "familytree"

urlpatterns = [
    path("", RelationshipListCreateAPIView.as_view(), name="relationship-list-create"),
    path("graph/", FamilyTreeGraphAPIView.as_view(), name="graph"),
    path("<int:pk>/", RelationshipDetailAPIView.as_view(), name="relationship-detail"),
]