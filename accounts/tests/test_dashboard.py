from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from items.models import Claim
from items.tests.helpers import make_item

User = get_user_model()


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        self.third_user = User.objects.create_user(username='thirduser', password='password123')
        self.url = reverse('dashboard')

    def test_dashboard_redirects_if_not_logged_in(self):
        """A visitor who is not logged in is redirected to the login page."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_dashboard_accessible_when_logged_in(self):
        """A logged-in user accesses the dashboard with my_items and my_claims in context."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard.html')
        self.assertIn('my_items', response.context)
        self.assertIn('my_claims', response.context)

    def test_dashboard_shows_only_own_items(self):
        """my_items lists only the items registered by the logged-in user."""
        own_item = make_item(self.user, title='Meu guarda-chuva')
        make_item(self.other_user, title='Item de outra pessoa')

        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['my_items']), [own_item])

    def test_dashboard_shows_only_own_claims(self):
        """my_claims lists only the claims submitted by the logged-in user."""
        own_item = make_item(self.user, title='Garrafa do usuário')
        other_item = make_item(self.other_user, title='Mochila de outro')
        own_claim = Claim.objects.create(item=other_item, claimant=self.user, message='É minha mochila')
        Claim.objects.create(item=other_item, claimant=self.third_user, message='Reivindicação de terceiro')
        Claim.objects.create(item=own_item, claimant=self.other_user, message='Reivindicação recebida')

        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(list(response.context['my_claims']), [own_claim])

    def test_pending_claims_count_counts_only_pending_claims(self):
        """pending_claims_count counts only pending claims (e.g. 2 pending + 1 rejected = 2)."""
        item = make_item(self.user, title='Chave do ICEx')
        Claim.objects.create(item=item, claimant=self.other_user, message='Pendente 1', status=Claim.Status.PENDING)
        Claim.objects.create(item=item, claimant=self.third_user, message='Pendente 2', status=Claim.Status.PENDING)
        Claim.objects.create(item=item, claimant=self.other_user, message='Recusada', status=Claim.Status.REJECTED)

        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        listed_item = response.context['my_items'].get(pk=item.pk)
        self.assertEqual(listed_item.pending_claims_count, 2)
        self.assertContains(response, '2 reivindicações pendentes')

    def test_pending_claims_count_excludes_accepted_and_rejected_claims(self):
        """An item with only accepted or rejected claims has pending_claims_count equal to zero."""
        item = make_item(self.user, title='Carteira preta')
        Claim.objects.create(item=item, claimant=self.other_user, message='Aceita', status=Claim.Status.ACCEPTED)
        Claim.objects.create(item=item, claimant=self.third_user, message='Recusada', status=Claim.Status.REJECTED)

        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        listed_item = response.context['my_items'].get(pk=item.pk)
        self.assertEqual(listed_item.pending_claims_count, 0)
        self.assertNotContains(response, 'reivindicação pendente')
        self.assertNotContains(response, 'reivindicações pendentes')
