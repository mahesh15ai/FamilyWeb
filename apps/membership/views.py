from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import FamilyMembership, RoleChoices
from .serializers import MembershipSerializer, RoleUpdateSerializer


@extend_schema(tags=["Membership"])
class MemberListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List members of my family", responses={200: MembershipSerializer(many=True)})
    def get(self, request):
        my_membership = services.get_membership_for_user(user=request.user)
        if not my_membership:
            return Response(
                {"message": _("You are not part of any family yet.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        members = services.list_family_members(family=my_membership.family)
        return Response(MembershipSerializer(members, many=True).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Membership"])
class MemberDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return FamilyMembership.objects.get(pk=pk)

    @extend_schema(summary="Get member details", responses={200: MembershipSerializer})
    def get(self, request, pk):
        membership = self.get_object(pk)
        return Response(MembershipSerializer(membership).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Remove a member from the family")
    def delete(self, request, pk):
        membership = self.get_object(pk)
        services.remove_member(actor=request.user, membership=membership)
        return Response({"message": _("Member removed successfully.")}, status=status.HTTP_200_OK)


@extend_schema(tags=["Membership"])
class MemberRoleUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change a member's role",
        request=RoleUpdateSerializer,
        responses={200: MembershipSerializer},
    )
    def patch(self, request, pk):
        membership = FamilyMembership.objects.get(pk=pk)
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = services.update_member_role(
            actor=request.user, membership=membership, new_role=serializer.validated_data["role"]
        )
        return Response(MembershipSerializer(updated).data, status=status.HTTP_200_OK)


@extend_schema(tags=["Membership"])
class RoleListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List available roles")
    def get(self, request):
        return Response(
            [{"value": choice.value, "label": choice.label} for choice in RoleChoices],
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Membership"],
    summary="Search members in my family",
    parameters=[
        OpenApiParameter(
            name="q",
            description="Search by first name, last name, or email",
            required=False,
            type=OpenApiTypes.STR,
        )
    ],
    responses={200: MembershipSerializer(many=True)},
)
class MemberSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "")
        members = services.search_family_members(actor=request.user, query=query)
        return Response(MembershipSerializer(members, many=True).data, status=status.HTTP_200_OK)