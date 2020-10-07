from rest_framework import permissions


class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class ScopesPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        required_scopes = self.get_scopes(request, view)
        if not required_scopes:
            # no required scopes found
            return True

        scopes = getattr(request.user, 'scopes', [])
        if not scopes:
            return False

        # any matched scope are allowed
        for required_scope in required_scopes:
            if frozenset(required_scope.split()).issubset(scopes):
                return True

        return False

    def get_scopes(self, request, view):
        try:
            return getattr(view, 'required_scopes')
        except AttributeError:
            raise AssertionError(
                'TokenHasScope requires the view to define '
                'the required_scopes attribute'
            )
