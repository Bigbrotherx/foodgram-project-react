from rest_framework import permissions


class MyPermission(metaclass=permissions.BasePermissionMetaclass):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return True
