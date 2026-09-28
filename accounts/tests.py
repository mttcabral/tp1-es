from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse('dashboard')

    def test_dashboard_redirects_if_not_logged_in(self):
        """Testa se o painel pessoal exige autenticação."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_dashboard_accessible_when_logged_in(self):
        """Testa se o painel carrega corretamente para usuário autenticado."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard.html')
        self.assertIn('my_items', response.context)
        self.assertIn('my_claims', response.context)
