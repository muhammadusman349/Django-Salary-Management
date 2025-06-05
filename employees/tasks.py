from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


@shared_task
def send_invitation_email_task(invitation_id, is_resend=False):
    from .models import EmployeeInvitation

    try:
        invitation = EmployeeInvitation.objects.select_related(
            'organization', 'position', 'invited_by'
        ).get(id=invitation_id)
    except EmployeeInvitation.DoesNotExist:
        return

    context = {
        'organization': invitation.organization.name,
        'position': invitation.position.title if invitation.position else 'N/A',
        'invited_by': invitation.invited_by.full_name,
        'acceptance_url': f"{settings.FRONTEND_URL}/accept-invitation?token={invitation.token}",
        'expires_at': invitation.expires_at.strftime("%B %d, %Y"),
    }

    if is_resend:
        subject = f"Join {context['organization']} - Invitation Reminder"
        template = 'emails/resendinvite.html'
    else:
        subject = f"Invitation to join {context['organization']}"
        template = 'emails/invitation.html'

    html_message = render_to_string(template, context)

    send_mail(
        subject=subject,
        message='This is an HTML email. Please use an HTML-compatible mail client.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.email],
        html_message=html_message,
        fail_silently=False
    )
