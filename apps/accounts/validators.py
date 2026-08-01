import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_password_strength(password: str) -> None:
    errors = []

    if len(password) < 8:
        errors.append(_("Password must be at least 8 characters long."))
    if not re.search(r"[A-Z]", password):
        errors.append(_("Password must contain at least one uppercase letter."))
    if not re.search(r"[a-z]", password):
        errors.append(_("Password must contain at least one lowercase letter."))
    if not re.search(r"[0-9]", password):
        errors.append(_("Password must contain at least one number."))
    if not re.search(r"[!@#$%^&*()\-_=+\[\]{};:'\",.<>/?\\|`~]", password):
        errors.append(_("Password must contain at least one special character."))

    if errors:
        raise ValidationError(errors)