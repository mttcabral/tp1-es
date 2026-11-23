from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from items.models import Claim, Item

from .helpers import make_item

User = get_user_model()


class ClaimCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.finder = User.objects.create_user(username='finder', password='password123')
        cls.claimant = User.objects.create_user(username='claimant', password='password123')
        cls.item = make_item(cls.finder)

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
        lost_item = make_item(self.finder, kind=Item.Kind.LOST)
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

    def test_duplicate_pending_claim_is_blocked(self):
        """A user cannot send a second claim while the first one on the same item is still pending."""
        Claim.objects.create(item=self.item, claimant=self.claimant, message='Primeira')
        response = self.post_claim(self.item, message='Segunda')
        self.assertRedirects(response, self.item.get_absolute_url())
        self.assertIn(
            'Você já tem uma reivindicação pendente para este item.',
            [str(m) for m in get_messages(response.wsgi_request)],
        )
        self.assertEqual(Claim.objects.count(), 1)

    def test_empty_message_shows_error_and_saves_nothing(self):
        """The claim message is required: an empty one shows an error and nothing is saved."""
        response = self.post_claim(self.item, message='')
        self.assert_rejected(
            response, self.item, 'Não foi possível enviar a reivindicação. A mensagem não pode ficar vazia.'
        )

    def test_whitespace_only_message_is_treated_as_empty(self):
        """A message made only of spaces counts as empty: the claim is rejected and nothing is saved."""
        response = self.post_claim(self.item, message='   ')
        self.assert_rejected(
            response, self.item, 'Não foi possível enviar a reivindicação. A mensagem não pode ficar vazia.'
        )

    def test_nonexistent_item_returns_404(self):
        """Claiming an item that does not exist returns 404."""
        response = self.client.post(reverse('claim_create', args=[9999]), {'message': 'É minha'})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Claim.objects.exists())

    def test_user_can_claim_again_after_rejection(self):
        """Only pending claims block a new one: after a rejection the user can claim the item again."""
        Claim.objects.create(
            item=self.item, claimant=self.claimant, message='Primeira', status=Claim.Status.REJECTED
        )
        response = self.post_claim(self.item, message='Tenho a nota fiscal')
        self.assertRedirects(response, self.item.get_absolute_url())
        self.assertEqual(Claim.objects.filter(status=Claim.Status.PENDING).count(), 1)
        self.assertEqual(Claim.objects.count(), 2)
