from rest_framework import generics, permissions, status
from .decorator import permission_required
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Department, Position, Employee
from .serializers import *
from accounts.models import User


class DepartmentView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all().order_by('-id')
    lookup_field = 'id'

    @permission_required(['view_department'])
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id', None)
        if id:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    @permission_required(['add_department'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @permission_required(['change_department'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @permission_required(['change_department'])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @permission_required(['delete_department'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PositionView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PositionSerializer
    queryset = Position.objects.all().order_by('-id')
    lookup_field = 'id'

    @permission_required(['view_position'])
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id',None)
        if id:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        department_id = self.request.query_params.get('department_id')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        return queryset

    @permission_required(['add_position'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @permission_required(['change_position'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @permission_required(['change_position'])
    def patch(self, request, *args, **kwargs):        
        return super().patch(request, *args, **kwargs)

    @permission_required(['delete_position'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class EmployeeView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.select_related('user', 'position', 'position__department').order_by('-id')
    lookup_field = 'id'

    @permission_required(['view_employee'])
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id',None)
        if id:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    @permission_required(['add_employee'])
    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, id=user_id)
        if hasattr(user, 'employee_profile'):
            return Response(
                {'error': 'User already has an employee profile'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(
            EmployeeSerializer(serializer.instance).data,
            status=status.HTTP_201_CREATED
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @permission_required(['change_employee'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @permission_required(['change_employee'])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @permission_required(['delete_employee'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
