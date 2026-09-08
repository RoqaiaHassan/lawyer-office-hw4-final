from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.dispatch import receiver


@receiver(user_logged_in)
def send_welcome_email_on_first_login(sender, request, user, **kwargs):
    if not user or not getattr(user, 'email', None):
        return

    if getattr(user, 'welcome_email_sent', False):
        return

    office_name = getattr(settings, 'OFFICE_NAME', 'Vision Law Office')
    display_name = user.get_full_name() or user.username
    subject = f'مرحبًا بك في {office_name}'
    message = (
        f'مرحبًا {display_name}،\n\n'
        f'يسعدنا أن نرحب بك في {office_name}.\n'
        f'اسمك: {display_name}\n'
        f'البريد الإلكتروني: {user.email}\n\n'
        'نتطلع لخدمتكم ومتابعتكم في كل خطوة.\n\n'
        f'{office_name}'
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL or None,
        [user.email],
        fail_silently=True,
    )

    user.welcome_email_sent = True
    user.save(update_fields=['welcome_email_sent'])
