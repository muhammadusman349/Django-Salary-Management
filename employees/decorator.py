from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import DepartmentRole, PositionRole, EmployeeRole, OrganizationRole


def permission_required(codes):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            user = request.user
            has_perm = (
                DepartmentRole.objects.filter(user=user, permission__code__in=codes).exists() or
                PositionRole.objects.filter(user=user, permission__code__in=codes).exists() or
                EmployeeRole.objects.filter(user=user, permission__code__in=codes).exists() or
                OrganizationRole.objects.filter(user=user, permission__code__in=codes).exists()
            )
            if not has_perm:
                return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator
