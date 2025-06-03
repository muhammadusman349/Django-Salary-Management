from django.contrib import admin
from .models import (Department, Position, Employee,
                     DepartmentPermission, PositionPermission,
                     EmployeePermission, DepartmentRole, PositionRole, EmployeeRole)

# Register your models here.

admin.site.register(Department)
admin.site.register(DepartmentPermission)
admin.site.register(DepartmentRole)
admin.site.register(Position)
admin.site.register(PositionPermission)
admin.site.register(PositionRole)
admin.site.register(Employee)
admin.site.register(EmployeePermission)
admin.site.register(EmployeeRole)
