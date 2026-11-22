from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from items.models import Claim, Item

User = get_user_model()


class ClaimCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.finder = User.objects.create_user(username='finder', password='password123')
        cls.claimant = User.objects.create_user(username='claimant', password='password123')
        cls.item = Item.objects.create(
            author=cls.finder,
            kind=Item.Kind.FOUND,
            title='Carteira marrom',
            description='Encontrada no banco da Praça de Serviços',
            category=Item.Category.WALLETS_BAGS,
            location=Item.Location.SERVICES_SQUARE,
        )

    def setUp(self):
        self.client.login(username='claimant', password='password123')

    def post_claim(self, item, message='Tem minha carteirinha da UFMG dentro'):
        return self.client.post(reverse('claim_create', args=[item.pk]), {'message': message})

    def assert_rejected(self, response, item, error):
        """The claim is refused: back to the item page, error shown and nothing saved."""
        self.assertRedirects(response, item.get_absolute_url())
        self.assertIn(error, [str(m) for m in get_messages(response.wsgi_request)])
        self.assertFalse(Claim.objects.filter(item=item, status=Claim.Status.PENDING).exists())

    def test_valid_claim_is_saved_as_pending(self):
        """A valid claim on someone else's open found item is saved as pending for the logged-in user."""
        response = self.post_claim(self.item)
        self.assertRedirects(response, self.item.get_absolute_url())
        claim = Claim.objects.get()
        self.assertEqual(claim.item, self.item)
        self.assertEqual(claim.claimant, self.claimant)
        self.assertEqual(claim.status, Claim.Status.PENDING)
        self.assertIn('Reivindicação enviada com sucesso!', [str(m) for m in get_messages(response.wsgi_request)])

    def test_anonymous_user_is_redirected_to_login(self):
        """A visitor who is not logged in is sent to the login page and no claim is saved."""
        self.client.logout()
        url = reverse('claim_create', args=[self.item.pk])
        response = self.client.post(url, {'message': 'É minha'})
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
        self.assertFalse(Claim.objects.exists())

    def test_lost_item_cannot_be_claimed(self):
        """Only found items can be claimed: a lost item was registered by its own owner."""
        lost_item = Item.objects.create(
            author=self.finder,
            kind=Item.Kind.LOST,
            title='Fone de ouvido',
            description='Perdido no CAD 2',
            category=Item.Category.ELECTRONICS,
            location=Item.Location.CAD2,
        )
        response = self.post_claim(lost_item)
        self.assert_rejected(response, lost_item, 'Só é possível reivindicar itens encontrados.')

    def test_user_cannot_claim_own_item(self):
        """The author of a found item cannot claim it."""
        self.client.login(username='finder', password='password123')
        response = self.post_claim(self.item)
        self.assert_rejected(response, self.item, 'Você não pode reivindicar um item que você mesmo cadastrou.')

    def test_resolved_item_cannot_be_claimed(self):
        """A resolved item no longer accepts claims."""
        self.item.status = Item.Status.RESOLVED
        self.item.save()
        response = self.post_claim(self.item)
        self.assert_rejected(response, self.item, 'Este item já foi resolvido e não pode mais ser reivindicado.')
