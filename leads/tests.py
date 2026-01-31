from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class DashboardViewTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='testuser', password='testpass')

	def test_dashboard_requires_login(self):
		response = self.client.get(reverse('dashboard'))
		self.assertNotEqual(response.status_code, 200)
		self.client.login(username='testuser', password='testpass')
		response = self.client.get(reverse('dashboard'))
		self.assertEqual(response.status_code, 200)
