from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from items.models import Claim, Item

from .helpers import make_item

User = get_user_model()


class ClaimActionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')
        self.third_user = User.objects.create_user(username='third', password='password123')
        
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

    def assert_non_pending_error(self, response, expected_claim_status, expected_item_status):
        """A non-pending claim cannot be accepted or rejected: shows error and changes nothing."""
        self.assertRedirects(response, self.item.get_absolute_url())
        self.assertIn('Esta reivindicação não está pendente.', [str(m) for m in get_messages(response.wsgi_request)])
        self.claim.refresh_from_db()
        self.item.refresh_from_db()
        self.assertEqual(self.claim.status, expected_claim_status)
        self.assertEqual(self.item.status, expected_item_status)

    def test_only_owner_can_accept_claim(self):
        """Only the item owner can accept a claim (non-owner gets 403)."""
        self.client.login(username='other', password='password123')
        response = self.client.post(self.accept_url)
        self.assertEqual(response.status_code, 403)
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, Claim.Status.PENDING)

    def test_owner_accepts_claim(self):
        """Accepting a claim marks it as accepted and resolves the item."""
        self.client.login(username='owner', password='password123')
        response = self.client.post(self.accept_url)
        
        self.claim.refresh_from_db()
        self.item.refresh_from_db()
        
        self.assertEqual(self.claim.status, Claim.Status.ACCEPTED)
        self.assertEqual(self.item.status, Item.Status.RESOLVED)
        self.assertRedirects(response, self.item.get_absolute_url())

    def test_owner_rejects_claim(self):
        """Rejecting a claim marks it as rejected and keeps the item open."""
        self.client.login(username='owner', password='password123')
        response = self.client.post(self.reject_url)
        
        self.claim.refresh_from_db()
        self.item.refresh_from_db()
        
        self.assertEqual(self.claim.status, Claim.Status.REJECTED)
        self.assertEqual(self.item.status, Item.Status.OPEN)
        self.assertRedirects(response, self.item.get_absolute_url())

    def test_accepting_claim_auto_rejects_other_pending_claims_on_same_item(self):
        """Accepting a claim rejects other pending claims on the same item without affecting other items."""
        other_claim = Claim.objects.create(item=self.item, claimant=self.third_user, message='Na verdade é minha')
        other_item = make_item(self.owner, title='Caderno vermelho')
        unrelated_claim = Claim.objects.create(item=other_item, claimant=self.third_user, message='É meu caderno')

        self.client.login(username='owner', password='password123')
        self.client.post(self.accept_url)

        other_claim.refresh_from_db()
        unrelated_claim.refresh_from_db()
        self.assertEqual(other_claim.status, Claim.Status.REJECTED)
        self.assertEqual(unrelated_claim.status, Claim.Status.PENDING)

    def test_accepting_rejected_claim_shows_error_and_changes_nothing(self):
        """Accepting a claim that is already rejected shows an error and leaves claim and item unchanged."""
        self.claim.status = Claim.Status.REJECTED
        self.claim.save()
        self.client.login(username='owner', password='password123')
        response = self.client.post(self.accept_url)
        self.assert_non_pending_error(response, Claim.Status.REJECTED, Item.Status.OPEN)

    def test_accepting_accepted_claim_shows_error_and_changes_nothing(self):
        """Accepting a claim that is already accepted shows an error and changes nothing."""
        self.claim.status = Claim.Status.ACCEPTED
        self.claim.save()
        self.item.status = Item.Status.RESOLVED
        self.item.save()
        self.client.login(username='owner', password='password123')
        response = self.client.post(self.accept_url)
        self.assert_non_pending_error(response, Claim.Status.ACCEPTED, Item.Status.RESOLVED)

    def test_rejecting_accepted_claim_shows_error_and_changes_nothing(self):
        """Rejecting a claim that is already accepted shows an error and leaves claim and item unchanged."""
        self.claim.status = Claim.Status.ACCEPTED
        self.claim.save()
        self.item.status = Item.Status.RESOLVED
        self.item.save()
        self.client.login(username='owner', password='password123')
        response = self.client.post(self.reject_url)
        self.assert_non_pending_error(response, Claim.Status.ACCEPTED, Item.Status.RESOLVED)

    def test_rejecting_rejected_claim_shows_error_and_changes_nothing(self):
        """Rejecting a claim that is already rejected shows an error and changes nothing."""
        self.claim.status = Claim.Status.REJECTED
        self.claim.save()
        self.client.login(username='owner', password='password123')
        response = self.client.post(self.reject_url)
        self.assert_non_pending_error(response, Claim.Status.REJECTED, Item.Status.OPEN)

    def test_only_owner_can_reject_claim(self):
        """Only the item owner can reject a claim (non-owner gets 403)."""
        self.client.login(username='other', password='password123')
        response = self.client.post(self.reject_url)
        self.assertEqual(response.status_code, 403)
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, Claim.Status.PENDING)

    def test_anonymous_user_accepting_claim_is_redirected_to_login(self):
        """A visitor who is not logged in is redirected to login when posting to accept a claim."""
        response = self.client.post(self.accept_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.accept_url}")
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, Claim.Status.PENDING)

    def test_anonymous_user_rejecting_claim_is_redirected_to_login(self):
        """A visitor who is not logged in is redirected to login when posting to reject a claim."""
        response = self.client.post(self.reject_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.reject_url}")
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, Claim.Status.PENDING)

    def test_accepting_nonexistent_claim_returns_404(self):
        """Accepting a claim that does not exist returns 404."""
        self.client.login(username='owner', password='password123')
        response = self.client.post(reverse('claim_accept', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_rejecting_nonexistent_claim_returns_404(self):
        """Rejecting a claim that does not exist returns 404."""
        self.client.login(username='owner', password='password123')
        response = self.client.post(reverse('claim_reject', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_get_on_accept_claim_returns_405(self):
        """Claim acceptance only accepts POST, so GET returns 405 Method Not Allowed."""
        self.client.login(username='owner', password='password123')
        response = self.client.get(self.accept_url)
        self.assertEqual(response.status_code, 405)
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, Claim.Status.PENDING)

    def test_get_on_reject_claim_returns_405(self):
        """Claim rejection only accepts POST, so GET returns 405 Method Not Allowed."""
        self.client.login(username='owner', password='password123')
        response = self.client.get(self.reject_url)
        self.assertEqual(response.status_code, 405)
        self.claim.refresh_from_db()
        self.assertEqual(self.claim.status, Claim.Status.PENDING)
