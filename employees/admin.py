from django.contrib import admin
from .models import (Department, Position, Employee,
                     DepartmentPermission, PositionPermission,
                     EmployeePermission, DepartmentRole,
                     PositionRole, EmployeeRole, Organization,
                     OrganizationPermission, OrganizationRole, EmployeeInvitation)

# Register your models here.


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'position', 'status', 'added_by', 'created_at', 'updated_at']
    search_fields = ['user', 'position', 'department_name', 'status', 'added_by']
    list_filter = ['status', 'is_active', 'is_on_leave']


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'admin', 'get_employees', 'created_at', 'updated_at']
    search_fields = ['name', 'admin']

    @admin.display(description='Employees')
    def get_employees(self, obj):
        return ", ".join([str(employee) for employee in obj.employees.all()[:3]])


class EmployeeInvitationAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'status', 'token', 'organization', 'position', 'invited_by', 'is_accepted', 'created_at', 'expires_at', 'last_sent_at']
    search_fields = ['email', 'organization', 'position', 'invited_by']
    list_filter = ['status', 'is_accepted']


admin.site.register(Department)
admin.site.register(DepartmentPermission)
admin.site.register(DepartmentRole)
admin.site.register(Position)
admin.site.register(PositionPermission)
admin.site.register(PositionRole)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeePermission)
admin.site.register(EmployeeRole)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationPermission)
admin.site.register(OrganizationRole)
admin.site.register(EmployeeInvitation, EmployeeInvitationAdmin)
