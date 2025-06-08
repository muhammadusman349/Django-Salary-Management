from rest_framework import serializers
from .models import Department, Position, Employee, Organization, EmployeeInvitation
from accounts.serializers import UserSerializer, UserProfileSerializer
from accounts.models import User


class DepartmentSerializer(serializers.ModelSerializer):
    lead = UserSerializer(read_only=True)
    lead_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='lead',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'lead', 'lead_id', 'created_at', 'updated_at']
        read_only_fields = ['lead', 'created_at', 'updated_at']


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Position
        fields = ['id', 'title', 'department', 'department_name','description', 'salary_range_min', 'salary_range_max', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    position_title = serializers.CharField(source='position.title', read_only=True)
    department_name = serializers.CharField(source='position.department.name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    tenure = serializers.IntegerField(read_only=True)
    added_by = serializers.CharField(source='added_by.full_name', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'added_by', 'position','position_title', 'department_name', 'status', 'date_of_birth', 'gender', 'marital_status',
                'nationality', 'address', 'city', 'state', 'country', 'postal_code', 'joining_date',
                'leaving_date', 'personal_email', 'personal_phone', 'emergency_contact_name',
                'emergency_contact_number', 'emergency_contact_relation', 'bank_name','age','tenure',
                'bank_account_number', 'is_active', 'is_on_leave', 'created_at', 'updated_at']
        read_only_fields = ['added_by', 'created_at', 'updated_at']

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


class OrganizationSerializer(serializers.ModelSerializer):
    admin_detail = serializers.SerializerMethodField(read_only=True)
    employees_detail = serializers.SerializerMethodField(read_only=True)
    admin_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='admin',
        write_only=True,
        required=False,
        allow_null=True
    )
    employee_ids = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employees',
        write_only=True,
        many=True,
        required=False
    )

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 
            'admin', 'admin_detail', 'admin_id',
            'employees', 'employees_detail', 'employee_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'admin', 'employees']

    def get_admin_detail(self, obj):
        if obj.admin:
            return {
                'id': obj.admin.id,
                'username': obj.admin.full_name,
                'first_name': obj.admin.first_name,
                'last_name': obj.admin.last_name,
                'email': obj.admin.email
            }
        return None

    def get_employees_detail(self, obj):
        return [{
            'id': emp.id,
            'first_name': emp.user.first_name,
            'last_name': emp.user.last_name,
            'position': emp.position.title if emp.position else None,
        } for emp in obj.employees.all()]


class EmployeeInvitationSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    position_title = serializers.CharField(source='position.title', read_only=True)
    department_name = serializers.CharField(source='position.department.name', read_only=True)

    class Meta:
        model = EmployeeInvitation
        fields = ['id', 'email', 'status', 'token', 'organization', 'organization_name', 'position', 'position_title', 'department_name', 'invited_by', 'is_accepted', 'created_at', 'expires_at', 'last_sent_at']
        read_only_fields = ['token', 'invited_by', 'is_accepted', 'created_at', 'expires_at', 'last_sent_at']


class EmployeeInvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    password = serializers.CharField(max_length=120, required=True, style={'input_type': 'password'}, write_only=True)
    accept = serializers.BooleanField()


class EmployeeResendInvitationSerializer(serializers.Serializer):
    invitation_id = serializers.IntegerField()


class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    added_by = serializers.CharField(source='added_by.full_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'user',
            'position',
            'status',
            'added_by',
            'date_of_birth',
            'gender',
            'marital_status',
            'nationality',
            'address',
            'city',
            'state',
            'country',
            'postal_code',
            'joining_date',
            'leaving_date',
            'personal_email',
            'personal_phone',
            'emergency_contact_name',
            'emergency_contact_number',
            'emergency_contact_relation',
            'bank_name',
            'bank_account_number',
            'is_active',
            'is_on_leave',
        ]
        read_only_fields = ['id', 'status', 'user', 'created_at', 'updated_at', 'is_active', 'leaving_date', 'position']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        # Update user
        user_serializer = UserProfileSerializer(instance=instance.user, data=user_data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        # Update employee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
