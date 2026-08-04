from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import User
from .validators import validate_password_strength


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email", "phone_number",
            "password", "confirm_password",
        ]

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("A user with this email already exists."))
        return value

    def validate_phone_number(self, value):
        if value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(_("A user with this phone number already exists."))
        return value

    def validate_password(self, value):
        validate_password_strength(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": _("Passwords do not match.")}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return User.objects.create_user(**validated_data)


class RegisterResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "uuid", "email", "first_name", "last_name"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise serializers.ValidationError(
                _("Invalid email or password."), code="authorization"
            )
        if not user.is_active:
            raise serializers.ValidationError(
                _("This account has been deactivated."), code="authorization"
            )

        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "uuid", "email", "first_name", "last_name", "full_name",
            "phone_number", "profile_photo", "date_of_birth", "gender",
            "bio", "is_verified", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "uuid", "email", "is_verified", "created_at", "updated_at"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "phone_number",
            "bio", "date_of_birth", "gender", "profile_photo",
        ]

    def validate_phone_number(self, value):
        qs = User.objects.filter(phone_number=value).exclude(pk=self.instance.pk)
        if value and qs.exists():
            raise serializers.ValidationError(_("This phone number is already in use."))
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Old password is incorrect."))
        return value

    def validate_new_password(self, value):
        validate_password_strength(value)
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": _("New passwords do not match.")}
            )
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": _("New password must be different from the old password.")}
            )
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_email(self, value):
        return value.lower().strip()

    def validate_new_password(self, value):
        validate_password_strength(value)
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": _("Passwords do not match.")}
            )
        return attrs