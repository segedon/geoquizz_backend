from rest_framework import permissions


class PlayInCategoryPermission(permissions.IsAuthenticated):
    message = 'you have not played a game in this category'

    def has_object_permission(self, request, view, obj):
        return request.user.games.filter(category=obj).exists()