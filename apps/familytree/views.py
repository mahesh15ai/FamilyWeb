from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Relationship
from .serializers import (
    RelationshipCreateSerializer,
    RelationshipSerializer,
    RelationshipUpdateSerializer,
)


@extend_schema(tags=["Family Tree"])
class RelationshipListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List relationships in my family", responses={200: RelationshipSerializer(many=True)})
    def get(self, request):
        relationships = services.list_family_relationships(actor=request.user)
        return Response(RelationshipSerializer(relationships, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a relationship",
        request=RelationshipCreateSerializer,
        responses={201: RelationshipSerializer},
    )
    def post(self, request):
        serializer = RelationshipCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        relationship = services.create_relationship(
            actor=request.user,
            from_member_id=serializer.validated_data["from_member"].id,
            to_member_id=serializer.validated_data["to_member"].id,
            relationship_type=serializer.validated_data["relationship_type"],
        )
        return Response(RelationshipSerializer(relationship).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Family Tree"])
class RelationshipDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return Relationship.objects.select_related("from_member", "to_member").get(pk=pk)

    @extend_schema(summary="Get relationship details", responses={200: RelationshipSerializer})
    def get(self, request, pk):
        relationship = self.get_object(pk)
        return Response(RelationshipSerializer(relationship).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a relationship's type",
        request=RelationshipUpdateSerializer,
        responses={200: RelationshipSerializer},
    )
    def patch(self, request, pk):
        relationship = self.get_object(pk)
        serializer = RelationshipUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = services.update_relationship(
            actor=request.user,
            relationship=relationship,
            relationship_type=serializer.validated_data["relationship_type"],
        )
        return Response(RelationshipSerializer(updated).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Delete a relationship")
    def delete(self, request, pk):
        relationship = self.get_object(pk)
        services.delete_relationship(actor=request.user, relationship=relationship)
        return Response({"message": _("Relationship deleted successfully.")}, status=status.HTTP_200_OK)


@extend_schema(tags=["Family Tree"])
class FamilyTreeGraphAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get the full family tree as nodes and edges")
    def get(self, request):
        graph = services.build_family_tree_graph(actor=request.user)
        return Response(graph, status=status.HTTP_200_OK)