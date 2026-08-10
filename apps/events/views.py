from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.membership.services import get_membership_for_user
from .models import Event
from .serializers import EventSerializer


class EventListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # GET /api/events/
    def get(self, request):
        membership = get_membership_for_user(user=request.user)
        if not membership or not membership.family:
            return Response({"count": 0, "results": []}, status=status.HTTP_200_OK)

        events = Event.objects.filter(family=membership.family)

        # Optional query filter: ?type=upcoming or ?type=past
        event_type = request.query_params.get("type")
        today = timezone.now().date()
        if event_type == "upcoming":
            events = events.filter(start_date__gte=today)
        elif event_type == "past":
            events = events.filter(start_date__lt=today)

        serializer = EventSerializer(events, many=True)
        return Response(
            {
                "count": events.count(),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # POST /api/events/
    def post(self, request):
        membership = get_membership_for_user(user=request.user)
        if not membership or not membership.family:
            return Response(
                {"detail": "You must belong to a family workspace to create events."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(family=membership.family, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id, user):
        membership = get_membership_for_user(user=user)
        if not membership or not membership.family:
            return None
        return get_object_or_404(Event, id=id, family=membership.family)

    # GET /api/events/{id}/
    def get(self, request, id):
        event = self.get_object(id, request.user)
        if not event:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT /api/events/{id}/
    def put(self, request, id):
        event = self.get_object(id, request.user)
        if not event:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /api/events/{id}/
    def delete(self, request, id):
        event = self.get_object(id, request.user)
        if not event:
            return Response(status=status.HTTP_404_NOT_FOUND)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)