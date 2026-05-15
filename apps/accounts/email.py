from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.accounts.utils import build_activation_link


def send_activation_email(request, user):
    activation_link = build_activation_link(request, user)
    context = {
        "user": user,
        "activation_link": activation_link,
        "app_name": "CodefortifyAuth",
    }
    subject = "Activate your account"
    text_body = render_to_string("accounts/email/activation_email.txt", context)
    html_body = render_to_string("accounts/email/activation_email.html", context)
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)


def send_welcome_email(user):
    context = {
        "user": user,
        "app_name": "CodefortifyAuth",
    }
    subject = "Welcome to CodefortifyAuth"
    text_body = render_to_string("accounts/email/welcome_email.txt", context)
    html_body = render_to_string("accounts/email/welcome_email.html", context)
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)
