from django.urls import path

from .views import (
    JoinRequestApproveAPIView,
    JoinRequestDetailAPIView,
    JoinRequestListCreateAPIView,
    JoinRequestRejectAPIView,
)

app_name = "joinrequests"

urlpatterns = [
    path("", JoinRequestListCreateAPIView.as_view(), name="join-request-list-create"),
    path("<int:pk>/", JoinRequestDetailAPIView.as_view(), name="join-request-detail"),
    path("<int:pk>/approve/", JoinRequestApproveAPIView.as_view(), name="join-request-approve"),
    path("<int:pk>/reject/", JoinRequestRejectAPIView.as_view(), name="join-request-reject"),
]