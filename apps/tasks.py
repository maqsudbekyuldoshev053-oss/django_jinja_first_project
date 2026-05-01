from celery import shared_task
from django.core.mail import send_mail

from root.settings import EMAIL_HOST_USER


@shared_task
def send_to_email(email, first_name, code):
    subject = 'Verification Code'
    message = f"{first_name} your code: {code}"
    send_mail(subject, message, EMAIL_HOST_USER, [email], fail_silently=False)
    return {'status': True, 'email': email, 'first_name': first_name}

