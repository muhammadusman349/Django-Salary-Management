from rest_framework import generics, permissions, status
from .decorator import permission_required
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Department, Position, Employee, Organization, EmployeeInvitation
from .serializers import *
from accounts.models import User
from datetime import timedelta
from django.conf import settings

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


class OrganizationView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all().order_by('-id')
    lookup_field = 'id'

    @permission_required(['view_organization'])
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id', None)
        if id:
            return self.retrieve(request, *args, **kwargs)
        else:
            return self.list(request, *args, **kwargs)

    @permission_required(['add_organization'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @permission_required(['change_organization'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @permission_required(['change_organization'])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @permission_required(['delete_organization'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SendInvitationView(generics.GenericAPIView):
    serializer_class = EmployeeInvitationSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        organization = serializer.validated_data['organization']

        # 1. Check if user already exists in the organization
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if organization.employees.filter(user=existing_user).exists():
                return Response(
                    {'error': 'User with this email is already a member of the organization.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 2. Check for pending invitations for this email in the same organization
        pending_invitations = EmployeeInvitation.objects.filter(
            email=email,
            organization=organization,
            status='pending',
            expires_at__gt=timezone.now()
        ).exists()

        if pending_invitations:
            return Response(
                {'error': 'A pending invitation already exists for this email in the organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Check if email was previously invited (regardless of status)
        previous_invitation = EmployeeInvitation.objects.filter(
            email=email,
            organization=organization
        ).order_by('-created_at').first()

        if previous_invitation:
            if previous_invitation.status == 'declined':
                return Response(
                    {'error': 'This email previously declined an invitation to this organization.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif previous_invitation.status == 'accepted':
                return Response(
                    {'error': 'This email previously accepted an invitation to this organization.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # All checks passed - create and send invitation
        invitation = serializer.save(
            invited_by=request.user,
            expires_at=timezone.now() + timedelta(days=7),
            last_sent_at=timezone.now(),
            status='pending'
        )

        # Send email
        self.send_invitation_email(invitation)

        return Response({
            'message': 'Invitation sent successfully.',
            'invitation_id': invitation.id,
            'token': invitation.token
        }, status=status.HTTP_201_CREATED)

    def send_invitation_email(self, invitation):
        subject = f"Invitation to join {invitation.organization.name}"
        acceptance_url = f"{settings.FRONTEND_URL}/accept-invitation?token={invitation.token}"

        message = render_to_string('emails/invitation.txt', {
            'organization': invitation.organization,
            'position': invitation.position,
            'invited_by': invitation.invited_by.get_full_name(),
            'acceptance_url': acceptance_url,
            'expires_at': invitation.expires_at.strftime("%B %d, %Y")
        })

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [invitation.email],
            fail_silently=False,
        )


class AcceptInvitationView(generics.GenericAPIView):
    serializer_class = EmployeeInvitationAcceptSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        user = request.user

        try:
            invitation = EmployeeInvitation.objects.get(
                token=token,
                is_accepted=False,
                expires_at__gt=timezone.now(),
                status='pending'
            )
        except EmployeeInvitation.DoesNotExist:
            return Response({'error': 'Invalid, expired, or already accepted invitation'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Ensure only intended user can accept if authenticated
        if user.is_authenticated and user.email != invitation.email:
            return Response({'error': 'This invitation was not sent to your email address.'},
                            status=status.HTTP_403_FORBIDDEN)

        if not serializer.validated_data.get('accept', False):
            invitation.status = 'declined'
            invitation.save()
            return Response({'message': 'Invitation declined'}, status=status.HTTP_200_OK)

        user_data = {
            'email': invitation.email,
            'first_name': serializer.validated_data.get('first_name', ''),
            'last_name': serializer.validated_data.get('last_name', '')
        }

        # Create or update user
        if not user.is_authenticated:
            user, created = User.objects.get_or_create(
                email=invitation.email,
                defaults=user_data
            )
            if created:
                user.set_password(serializer.validated_data['password'])
                user.save()
        else:
            for field, value in user_data.items():
                if value and not getattr(user, field):
                    setattr(user, field, value)
            if 'password' in serializer.validated_data:
                user.set_password(serializer.validated_data['password'])
            user.save()
            created = False

        # Prevent duplicate employee entry
        if Employee.objects.filter(user=user, members_of_organization=invitation.organization).exists():
            return Response({'error': 'User already belongs to this organization'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create employee record
        employee, employee_created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'position': invitation.position,
                'status': 'ACTIVE',
                'joining_date': timezone.now().date()
            }
        )

        # Add employee to org
        invitation.organization.employees.add(employee)

        # Finalize invitation
        invitation.is_accepted = True
        invitation.status = 'accepted'
        invitation.save()

        return Response({
            'message': 'Invitation accepted successfully',
            'user_id': user.id,
            'employee_id': employee.id,
            'user_created': created,
            'employee_created': employee_created
        }, status=status.HTTP_200_OK)


class ResendInvitationView(generics.GenericAPIView):
    serializer_class = EmployeeResendInvitationSerializer
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            invitation = EmployeeInvitation.objects.select_related(
                'organization', 'position', 'invited_by'
            ).get(
                id=serializer.validated_data['invitation_id'],
                invited_by=request.user,
                status__in=['pending', 'declined'],
                is_accepted=False
            )
        except EmployeeInvitation.DoesNotExist:
            return Response(
                {'error': 'Invalid invitation or already accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle expired or declined invitations
        if invitation.is_expired or invitation.status == 'declined':
            invitation.status = 'pending'
            invitation.save()

        # Resend the invitation
        invitation = invitation.resend()

        # Send invitation email
        send_mail(
            subject=f"Join {invitation.organization.name} - Invitation Reminder",
            message=render_to_string('emails/invitation_reminder.txt', {
                'organization': invitation.organization.name,
                'position': invitation.position.title if invitation.position else '',
                'invited_by': invitation.invited_by.get_full_name(),
                'acceptance_url': f"{settings.FRONTEND_URL}/accept-invitation?token={invitation.token}",
                'expires_at': invitation.expires_at.strftime("%B %d, %Y")
            }),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )

        return Response(
            {
                'message': 'Invitation resent successfully',
                'email': invitation.email,
                'new_expiration': invitation.expires_at,
                'status': invitation.status
            },
            status=status.HTTP_200_OK
        )
