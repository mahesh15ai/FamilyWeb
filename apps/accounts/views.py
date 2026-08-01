from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    RegisterResponseSerializer,
    RegisterSerializer,
)


@extend_schema(
    tags=["Authentication"],
    summary="Register a new user",
    description="Creates a new FamilyHub account. Email must be unique.",
    request=RegisterSerializer,
    responses={201: RegisterResponseSerializer},
    examples=[
        OpenApiExample(
            "Register request",
            value={
                "first_name": "Mahesh",
                "last_name": "Gomaskar",
                "email": "mahesh@gmail.com",
                "phone_number": "9876543210",
                "password": "Mahesh@123",
                "confirm_password": "Mahesh@123",
            },
            request_only=True,
        ),
    ],
)
class RegisterAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.register_user(validated_data=serializer.validated_data)
        return Response(
            {
                "message": _("Registration successful"),
                "user": RegisterResponseSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Authentication"],
    summary="Login",
    description="Authenticates a user with email/password and returns a JWT access/refresh pair.",
    request=LoginSerializer,
)
class LoginAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = services.login_user(user=serializer.validated_data["user"])
        return Response(
            {
                "access": result["access"],
                "refresh": result["refresh"],
                "user": ProfileSerializer(result["user"]).data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Authentication"],
    summary="Logout",
    description="Blacklists the provided refresh token, invalidating the current session.",
    request=LogoutSerializer,
)
class LogoutAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.logout_user(refresh_token=serializer.validated_data["refresh"])
        return Response({"message": _("Logged out successfully.")}, status=status.HTTP_200_OK)


@extend_schema(tags=["Authentication"])
class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(summary="Get current user's profile", responses={200: ProfileSerializer})
    def get(self, request):
        return Response(ProfileSerializer(request.user).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update current user's profile",
        request={"multipart/form-data": ProfileUpdateSerializer},
        responses={200: ProfileSerializer},
    )
    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            instance=request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = services.update_profile(user=request.user, validated_data=serializer.validated_data)
        return Response(ProfileSerializer(user).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Authentication"],
    summary="Change password",
    description="Changes the authenticated user's password after validating the old one.",
    request=ChangePasswordSerializer,
)
class ChangePasswordAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        services.change_password(
            user=request.user, new_password=serializer.validated_data["new_password"]
        )
        return Response({"message": _("Password changed successfully.")}, status=status.HTTP_200_OK)