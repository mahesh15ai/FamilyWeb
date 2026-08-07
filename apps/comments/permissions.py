from rest_framework import permissions


class IsCommentAuthorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Author can edit or delete
        if obj.author == request.user:
            return True

        # Admins can delete
        if request.method == "DELETE":
            user_membership = getattr(request.user, "family_membership", None)
            if user_membership and user_membership.role in ["OWNER", "SUPER_ADMIN"]:
                return True

        return False