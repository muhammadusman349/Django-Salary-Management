from django.urls import path
from . import views
from .models import setup_permissions

urlpatterns = [
    # Department URLs
    path('departments/', views.DepartmentView.as_view(), name='department-list'),
    path('departments/<int:id>/', views.DepartmentView.as_view(), name='department-detail'),

    # Position URLs
    path('positions/', views.PositionView.as_view(), name='position-list'),
    path('positions/<int:id>/', views.PositionView.as_view(), name='position-detail'),

    # Employee URLs
    path('employees/', views.EmployeeView.as_view(), name='employee-list'),
    path('employees/<int:id>/', views.EmployeeView.as_view(), name='employee-detail'),
]

setup_permissions()
