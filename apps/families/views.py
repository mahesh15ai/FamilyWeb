from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Family
from .serializers import (
    FamilyCreateSerializer,
    FamilySerializer,
    FamilyUpdateSerializer,
)


@extend_schema(tags=["Families"])
class FamilyListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(summary="List all families", responses={200: FamilySerializer(many=True)})
    def get(self, request):
        families = Family.objects.all()
        return Response(FamilySerializer(families, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Create a family",
        request={"multipart/form-data": FamilyCreateSerializer},
        responses={201: FamilySerializer},
    )
    def post(self, request):
        serializer = FamilyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        family = services.create_family(user=request.user, validated_data=serializer.validated_data)
        return Response(FamilySerializer(family).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Families"])
class FamilyDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_object(self, pk):
        return Family.objects.get(pk=pk)

    @extend_schema(summary="Get family details", responses={200: FamilySerializer})
    def get(self, request, pk):
        family = self.get_object(pk)
        return Response(FamilySerializer(family).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update a family",
        request={"multipart/form-data": FamilyUpdateSerializer},
        responses={200: FamilySerializer},
    )
    def patch(self, request, pk):
        family = self.get_object(pk)
        serializer = FamilyUpdateSerializer(instance=family, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = services.update_family(
            family=family, user=request.user, validated_data=serializer.validated_data
        )
        return Response(FamilySerializer(updated).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Delete a family")
    def delete(self, request, pk):
        family = self.get_object(pk)
        services.delete_family(family=family, user=request.user)
        return Response({"message": _("Family deleted successfully.")}, status=status.HTTP_200_OK)


@extend_schema(tags=["Families"])
class MyFamilyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get the logged-in user's family", responses={200: FamilySerializer})
    def get(self, request):
        family = services.get_my_family(user=request.user)
        if not family:
            return Response(
                {"message": _("You have not created or joined a family yet.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(FamilySerializer(family).data, status=status.HTTP_200_OK)