from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from apps.settings_app.models import SiteSettings


@shared_task
def send_contact_email(name, email, subject, message):
    """Deliver a Contact-form submission to the editorial inbox.

    Dispatched via .delay() so the request doesn't block on SMTP
    (CLAUDE.md ch.13 "Celery Tasks — Email sending"). In development
    CELERY_TASK_ALWAYS_EAGER runs this inline against the console email
    backend; in production it runs asynchronously against real SMTP.
    """

    site_settings = SiteSettings.get_solo()
    recipient = site_settings.contact_email or settings.DEFAULT_FROM_EMAIL
    if not recipient:
        return

    send_mail(
        subject=f'[Əlaqə formu] {subject}',
        message=f'Göndərən: {name} <{email}>\n\n{message}',
        from_email=settings.DEFAULT_FROM_EMAIL or email,
        recipient_list=[recipient],
    )
