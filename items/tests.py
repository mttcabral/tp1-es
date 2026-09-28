from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from items.models import Item, Claim

User = get_user_model()

class ClaimActionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')
        
        self.item = Item.objects.create(
            author=self.owner,
            title='Mochila Azul',
            description='Encontrada no CAD',
            kind=Item.Kind.FOUND,
            category=Item.Category.WALLETS_BAGS,
            location=Item.Location.CAD1,
            status=Item.Status.OPEN
        )
        
        self.claim = Claim.objects.create(
            item=self.item,
            claimant=self.other_user,
            message='É minha mochila!',
            status=Claim.Status.PENDING
        )
        
        self.accept_url = reverse('claim_accept', args=[self.claim.pk])
        self.reject_url = reverse('claim_reject', args=[self.claim.pk])

    def test_only_owner_can_accept_claim(self):
        """Testa se apenas o dono do item pode aceitar a reivindicação (retorna 403 se não for o dono)."""
        self.client.login(username='other', password='password123')
        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, 403)

    def test_owner_accepts_claim(self):
        """Testa se aceitar a reivindicação resolve o item e a marca como aceita."""
        self.client.login(username='owner', password='password123')
        response = self.client.post(self.accept_url)
        
        self.claim.refresh_from_db()
        self.item.refresh_from_db()
        
        self.assertEqual(self.claim.status, Claim.Status.ACCEPTED)
        self.assertEqual(self.item.status, Item.Status.RESOLVED)
        self.assertRedirects(response, self.item.get_absolute_url())

    def test_owner_rejects_claim(self):
        """Testa se recusar a reivindicação a marca como recusada e mantém o item aberto."""
        self.client.login(username='owner', password='password123')
        response = self.client.post(self.reject_url)
        
        self.claim.refresh_from_db()
        self.item.refresh_from_db()
        
        self.assertEqual(self.claim.status, Claim.Status.REJECTED)
        self.assertEqual(self.item.status, Item.Status.OPEN)
