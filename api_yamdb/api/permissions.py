from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.urls import reverse


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moder

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsYourself(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if reverse('users-me') in request.build_absolute_uri():
            if request.method in ['GET', 'DELETE']:
                return True
            elif request.method == 'PATCH':
                if 'role' not in request.data:
                    return True
        return False
