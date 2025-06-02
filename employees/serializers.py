from rest_framework import serializers
from .models import Department, Position, Employee
from accounts.serializers import UserSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'description', 'lead', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Position
        fields = ('id', 'title', 'department', 'department_name','description', 'salary_range_min', 'salary_range_max', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    position_title = serializers.CharField(source='position.title', read_only=True)
    department_name = serializers.CharField(source='position.department.name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    tenure = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'position','position_title', 'department_name', 'status', 'date_of_birth', 'gender', 'marital_status',
                'nationality', 'address', 'city', 'state', 'country', 'postal_code', 'joining_date',
                'leaving_date', 'personal_email', 'personal_phone', 'emergency_contact_name',
                'emergency_contact_number', 'emergency_contact_relation', 'bank_name','age','tenure',
                'bank_account_number', 'is_active', 'is_on_leave', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        if user_data:
            user_serializer = UserSerializer(
                instance.user,
                data=user_data,
                partial=True
            )
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        return super().update(instance, validated_data)
