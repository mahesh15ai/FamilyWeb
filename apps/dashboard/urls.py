from django.urls import path

from .views import (
    DashboardBirthdaysAPIView,
    DashboardOverviewAPIView,
    DashboardRecentActivitiesAPIView,
    DashboardStatisticsAPIView,
    DashboardUpcomingEventsAPIView,
)

urlpatterns = [
    path("", DashboardOverviewAPIView.as_view(), name="dashboard-overview"),
    path("statistics/", DashboardStatisticsAPIView.as_view(), name="dashboard-statistics"),
    path("recent-activities/", DashboardRecentActivitiesAPIView.as_view(), name="dashboard-recent-activities"),
    path("upcoming-events/", DashboardUpcomingEventsAPIView.as_view(), name="dashboard-upcoming-events"),
    path("birthdays/", DashboardBirthdaysAPIView.as_view(), name="dashboard-birthdays"),
]