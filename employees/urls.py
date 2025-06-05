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

    # Organization URLs
    path('organizations/', views.OrganizationView.as_view(), name='organization-list'),
    path('organizations/<int:id>/', views.OrganizationView.as_view(), name='organization-detail'),

    # Invitation URLs
    path('invitations/send/', views.SendInvitationView.as_view(), name='send-invitation'),
    path('invitations/accept/', views.AcceptInvitationView.as_view(), name='accept-invitation'),
    path('invitations/resend/', views.ResendInvitationView.as_view(), name='resend-invitation'),

    # Employee Invitation List View
    path('employee-invitations/list/', views.EmployeeInvitationListView.as_view(), name='employee-invitation-list'),
    path('employee-invitations/list/<int:id>/', views.EmployeeInvitationListView.as_view(), name='employee-invitation-detail'),

    # Employee Profile View
    path('employee/profile/', views.EmployeeProfileView.as_view(), name='employee-profile'),
    
]

setup_permissions()
