from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    BirthdaysSerializer,
    DashboardOverviewSerializer,
    DashboardStatisticsSerializer,
    RecentActivitySerializer,
    UpcomingEventsSerializer,
)


@extend_schema(tags=["Dashboard"])
class DashboardOverviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get Dashboard Overview", responses={200: DashboardOverviewSerializer})
    def get(self, request):
        family = services.get_user_family(request.user)
        data = services.get_overview_data(family)
        return Response(DashboardOverviewSerializer(data).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Dashboard"])
class DashboardStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get Dashboard Statistics", responses={200: DashboardStatisticsSerializer})
    def get(self, request):
        family = services.get_user_family(request.user)
        data = services.get_statistics_data(family)
        return Response(DashboardStatisticsSerializer(data).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Dashboard"])
class DashboardRecentActivitiesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get Recent Activities Feed", responses={200: RecentActivitySerializer})
    def get(self, request):
        family = services.get_user_family(request.user)
        data = services.get_recent_activities_data(family)
        return Response(RecentActivitySerializer(data).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Dashboard"])
class DashboardUpcomingEventsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get Upcoming Events", responses={200: UpcomingEventsSerializer})
    def get(self, request):
        family = services.get_user_family(request.user)
        data = services.get_upcoming_events_data(family)
        return Response(UpcomingEventsSerializer(data).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Dashboard"])
class DashboardBirthdaysAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get Upcoming Birthdays", responses={200: BirthdaysSerializer})
    def get(self, request):
        family = services.get_user_family(request.user)
        data = services.get_upcoming_birthdays_data(family)
        return Response(BirthdaysSerializer(data).data, status=status.HTTP_200_OK)