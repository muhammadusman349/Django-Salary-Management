from django.contrib import admin
from .models import Department, Position, Employee

# Register your models here.

admin.site.register(Department)
admin.site.register(Position)
admin.site.register(Employee)
