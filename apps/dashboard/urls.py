from django.urls import path

from .views import (
    DashboardBirthdaysAPIView,
    DashboardOverviewAPIView,
    DashboardRecentActivitiesAPIView,
    DashboardStatisticsAPIView,
    DashboardUpcomingEventsAPIView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardOverviewAPIView.as_view(), name="overview"),
    path("statistics/", DashboardStatisticsAPIView.as_view(), name="statistics"),
    path("recent-activities/", DashboardRecentActivitiesAPIView.as_view(), name="recent-activities"),
    path("upcoming-events/", DashboardUpcomingEventsAPIView.as_view(), name="upcoming-events"),
    path("birthdays/", DashboardBirthdaysAPIView.as_view(), name="birthdays"),
]