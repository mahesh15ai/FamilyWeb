from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PasswordResetOTP, User

OTP_LIFETIME_MINUTES = 10


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


def request_password_reset(*, email: str) -> None:
    """
    Generates a 6-digit OTP, stores only its hash, and emails the raw
    code to the user. Always succeeds silently if the email isn't
    registered — this prevents leaking which emails have accounts.
    """
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return

    otp = get_random_string(6, allowed_chars="0123456789")

    PasswordResetOTP.objects.create(
        user=user,
        otp_hash=make_password(otp),
        expires_at=timezone.now() + timedelta(minutes=OTP_LIFETIME_MINUTES),
    )

    send_mail(
        subject="Your FamilyHub password reset code",
        message=(
            f"Your password reset code is: {otp}\n\n"
            f"This code expires in {OTP_LIFETIME_MINUTES} minutes. "
            "If you didn't request this, you can safely ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def confirm_password_reset(*, email: str, otp: str, new_password: str) -> None:
    """
    Validates the OTP (must be unused, unexpired, and match the hash)
    and sets the new password. Marks the OTP used so it can't be
    replayed, and invalidates any other outstanding OTPs for this user.
    """
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        raise ValidationError({"otp": _("Invalid or expired code.")})

    candidate_otp = None
    for otp_record in PasswordResetOTP.objects.filter(
        user=user, is_used=False, expires_at__gt=timezone.now()
    ):
        if check_password(otp, otp_record.otp_hash):
            candidate_otp = otp_record
            break

    if not candidate_otp:
        raise ValidationError({"otp": _("Invalid or expired code.")})

    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])

    candidate_otp.is_used = True
    candidate_otp.save(update_fields=["is_used"])

    # Invalidate any other still-pending OTPs for this user.
    PasswordResetOTP.objects.filter(user=user, is_used=False).exclude(pk=candidate_otp.pk).update(is_used=True)