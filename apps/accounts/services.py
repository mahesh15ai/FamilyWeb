from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


def register_user(*, validated_data: dict) -> User:
    """
    Creates a new user. Password hashing is handled inside
    User.objects.create_user via the manager.
    """
    validated_data.pop("confirm_password", None)
    return User.objects.create_user(**validated_data)


def issue_tokens_for_user(*, user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def login_user(*, user: User) -> dict:
    """
    Given an already-authenticated user (see LoginSerializer.validate),
    issues a fresh access/refresh token pair.
    """
    tokens = issue_tokens_for_user(user=user)
    return {**tokens, "user": user}


def logout_user(*, refresh_token: str) -> None:
    """
    Blacklists the given refresh token so it can no longer be used
    to obtain new access tokens.
    """
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError as exc:
        raise ValidationError({"refresh": _("Invalid or expired refresh token.")}) from exc


def update_profile(*, user: User, validated_data: dict) -> User:
    for field, value in validated_data.items():
        setattr(user, field, value)
    user.full_clean(exclude=["password"])
    user.save()
    return user


def change_password(*, user: User, new_password: str) -> User:
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    return user