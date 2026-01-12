from rest_framework import permissions


class IsApproved(permissions.BasePermission):
    def has_permission(self, request, view):
        # Tout le monde est approuvé → il suffit d'être authentifié
        return request.user.is_authenticated


class IsVendeurApproved(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'VENDEUR'
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'