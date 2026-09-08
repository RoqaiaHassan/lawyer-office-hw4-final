from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


class AuthFlowTests(TestCase):
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_first_login_sends_welcome_email_only_once(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='StrongPass123!'
        )

        mail.outbox.clear()

        self.client.login(username='newuser', password='StrongPass123!')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Vision Law Office', mail.outbox[0].subject + ' ' + mail.outbox[0].body)
        self.assertIn('newuser', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['newuser@example.com'])

        self.client.logout()
        self.client.login(username='newuser', password='StrongPass123!')
        self.assertEqual(len(mail.outbox), 1)

    def test_root_redirects_anonymous_user_to_registration(self):
        response = self.client.get(reverse('lawyer:home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account:register'))

    def test_admin_can_manage_lawyers(self):
        User = get_user_model()
        admin = User.objects.create_user(username='admin2', email='admin2@example.com', password='StrongPass123!')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        self.client.force_login(admin)
        response = self.client.get(reverse('lawyer:lawyer_list'))
        self.assertEqual(response.status_code, 200)
