from django.urls import path

from .views import (
    MemberDetailAPIView,
    MemberListAPIView,
    MemberRoleUpdateAPIView,
    MemberSearchAPIView,
    RoleListAPIView,
)

app_name = "membership"

urlpatterns = [
    path("", MemberListAPIView.as_view(), name="member-list"),
    path("roles/", RoleListAPIView.as_view(), name="role-list"),
    path("search/", MemberSearchAPIView.as_view(), name="member-search"),
    path("<int:pk>/", MemberDetailAPIView.as_view(), name="member-detail"),
    path("<int:pk>/role/", MemberRoleUpdateAPIView.as_view(), name="member-role-update"),
]