import logging

# Django core imports
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Local imports
from ..models import Business
from ..forms import ContactMessageForm

logger = logging.getLogger(__name__)

@require_POST
def submit_contact_form(request, business_subdirectory):
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    business = get_object_or_404(Business, subdirectory=business_subdirectory)
    form = ContactMessageForm(request.POST)

    if form.is_valid():
        try:
            # Save the message
            message = form.save(commit=False)
            message.business = business
            message.save()

            # Prepare email context
            context = {
                'business_name': business.business_name,
                'name': form.cleaned_data['name'],
                'email': form.cleaned_data['email'],
                'subject': form.cleaned_data['subject'],
                'message': form.cleaned_data['message'],
            }

            # Render email templates
            html_message = render_to_string('emails/contact_form_notification.html', context)
            text_message = render_to_string('emails/contact_form_notification.txt', context)

            # Send email using configured backend
            send_mail(
                subject=f'New Contact Form Message - {business.business_name}',
                message=text_message,
                from_email=f'noreply@{settings.MAILGUN_SERVER_NAME}' if settings.MAILGUN_SERVER_NAME else settings.DEFAULT_FROM_EMAIL,
                recipient_list=[business.email],
                html_message=html_message,
                fail_silently=False,
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Your message has been sent successfully!'
            })

        except Exception as e:
            # Log the error (you should have proper logging configured)
            logger.error(f'Error sending contact form email: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': 'There was an error sending your message. Please try again later.'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'errors': form.errors
    }, status=400)