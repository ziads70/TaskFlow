from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .models import User


class RegisterPageTests(SimpleTestCase):
    def test_register_page_is_available(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_root_register_alias_is_available(self):
        response = self.client.get('/register/')
        self.assertEqual(response.status_code, 200)

    def test_login_page_is_available(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)


class LoginRedirectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='test-password-123',
        )

    def test_successful_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user.username,
            'password': 'test-password-123',
        })

        self.assertRedirects(response, reverse('dashboard:dashboard'))

    def test_successful_login_respects_safe_next_url(self):
        dashboard_url = reverse('dashboard:dashboard')
        response = self.client.post(
            f"{reverse('accounts:login')}?next={dashboard_url}",
            {
                'username': self.user.username,
                'password': 'test-password-123',
                'next': dashboard_url,
            },
        )

        self.assertRedirects(response, dashboard_url)
