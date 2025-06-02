from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Department, Position, Employee
from .serializers import *
from accounts.models import User


class DepartmentView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    serializer_class = DepartmentSerializer
    lookup_field = 'id'
    queryset = Department.objects.all().order_by('-id')

    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id',None)
        if id:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)


class PositionView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    serializer_class = PositionSerializer
    lookup_field = 'id'
    queryset = Position.objects.all().order_by('-id')

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


class EmployeeView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []
    lookup_field = 'id'
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.select_related('user', 'position', 'position__department').order_by('-id')

    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id',None)
        if id:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

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