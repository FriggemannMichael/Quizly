from rest_framework.permissions import BasePermission


class IsQuizOwner(BasePermission):
    """Allow access to a quiz only for the user who owns it."""

    def has_object_permission(self, request, view, obj):
        """Return whether the request user owns the quiz."""
        return obj.owner_id == request.user.id
