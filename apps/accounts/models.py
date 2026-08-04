import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


def profile_photo_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"profile_photos/{instance.uuid}.{ext}"


class GenderChoices(models.TextChoices):
    MALE = "MALE", _("Male")
    FEMALE = "FEMALE", _("Female")
    OTHER = "OTHER", _("Other")
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY", _("Prefer not to say")


phone_validator = RegexValidator(
    regex=r"^\+?[0-9]{10,15}$",
    message=_("Enter a valid phone number (10-15 digits, optional leading +)."),
)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model. Email is the unique login identifier.
    No username field is used.
    """

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    email = models.EmailField(_("email address"), unique=True, db_index=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)

    phone_number = models.CharField(
        max_length=15, unique=True, null=True, blank=True,
        validators=[phone_validator], db_index=True,
    )

    profile_photo = models.ImageField(upload_to=profile_photo_path, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GenderChoices.choices, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        db_table = "users"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["uuid"]),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class PasswordResetOTP(models.Model):
    """
    A short-lived, single-use one-time code emailed to a user who has
    forgotten their password. The raw OTP is never stored — only its
    hash — same principle as password storage.
    """

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_otps"
    )
    otp_hash = models.CharField(max_length=128)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "password_reset_otps"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_used"])]

    def __str__(self):
        return f"OTP for {self.user.email} (used={self.is_used})"