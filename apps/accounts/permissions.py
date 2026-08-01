from rest_framework.permissions import BasePermission


class IsOwnerProfile(BasePermission):
    """
    Object-level permission: only the profile's own user can
    view/edit it. Used for endpoints that take a user pk/uuid,
    as opposed to /profile/ which implicitly uses request.user.
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class IsVerifiedUser(BasePermission):
    """
    Restricts access to users who have verified their account
    (e.g. via email verification, added in a later module).
    """

    message = "Your account is not verified yet."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)