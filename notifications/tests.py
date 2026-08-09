from django.test import SimpleTestCase
from django.urls import reverse


class HomePageTests(SimpleTestCase):
    def test_home_route_exists(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_notifications_home_route_exists(self):
        response = self.client.get(reverse('notifications:home'))
        self.assertEqual(response.status_code, 200)
