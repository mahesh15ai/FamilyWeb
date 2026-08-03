from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import JoinRequest
from .serializers import JoinRequestCreateSerializer, JoinRequestSerializer


@extend_schema(tags=["Join Requests"])
class JoinRequestListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List join requests for my family",
        description="Owner/super-admin scoped — returns pending and past requests for the family the actor administers.",
        responses={200: JoinRequestSerializer(many=True)},
    )
    def get(self, request):
        join_requests = services.list_join_requests_for_actor(actor=request.user)
        return Response(
            JoinRequestSerializer(join_requests, many=True).data, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Request to join a family",
        request=JoinRequestCreateSerializer,
        responses={201: JoinRequestSerializer},
    )
    def post(self, request):
        serializer = JoinRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        join_request = services.create_join_request(
            user=request.user, family_code=serializer.validated_data["family_code"]
        )
        return Response(
            JoinRequestSerializer(join_request).data, status=status.HTTP_201_CREATED
        )


@extend_schema(tags=["Join Requests"])
class JoinRequestDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(JoinRequest, pk=pk)

    @extend_schema(summary="Get join request details", responses={200: JoinRequestSerializer})
    def get(self, request, pk):
        join_request = self.get_object(pk)
        join_request = services.get_join_request_for_actor_or_raise(
            actor=request.user, join_request=join_request
        )
        return Response(JoinRequestSerializer(join_request).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Withdraw or delete a join request")
    def delete(self, request, pk):
        join_request = self.get_object(pk)
        services.withdraw_or_delete_join_request(actor=request.user, join_request=join_request)
        return Response(
            {"message": _("Join request removed successfully.")}, status=status.HTTP_200_OK
        )


@extend_schema(tags=["Join Requests"])
class JoinRequestApproveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Approve a join request", responses={200: JoinRequestSerializer})
    def patch(self, request, pk):
        join_request = get_object_or_404(JoinRequest, pk=pk)
        join_request = services.approve_join_request(actor=request.user, join_request=join_request)
        return Response(JoinRequestSerializer(join_request).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Join Requests"])
class JoinRequestRejectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Reject a join request", responses={200: JoinRequestSerializer})
    def patch(self, request, pk):
        join_request = get_object_or_404(JoinRequest, pk=pk)
        join_request = services.reject_join_request(actor=request.user, join_request=join_request)
        return Response(JoinRequestSerializer(join_request).data, status=status.HTTP_200_OK)