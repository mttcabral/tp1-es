from django.contrib.auth import get_user_model
from django.test import TestCase

from items.models import Claim, Item

from .helpers import make_item

User = get_user_model()


class ItemDetailContextTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.finder = User.objects.create_user(username='finder', password='password123')
        cls.claimant = User.objects.create_user(username='claimant', password='password123')
        cls.found_item = make_item(cls.finder)
        cls.lost_item = make_item(cls.finder, kind=Item.Kind.LOST)

    def get_detail(self, item, username=None):
        if username:
            self.client.login(username=username, password='password123')
        return self.client.get(item.get_absolute_url())

    def test_anonymous_user_gets_no_claim_form(self):
        """A visitor who is not logged in gets no claim form, pending flag or received claims."""
        response = self.get_detail(self.found_item)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('claim_form', response.context)
        self.assertNotIn('has_pending_claim', response.context)
        self.assertNotIn('received_claims', response.context)

    def test_has_pending_claim_is_false_without_claim(self):
        """A logged-in user with no claim on the item gets the form and has_pending_claim False."""
        response = self.get_detail(self.found_item, 'claimant')
        self.assertIn('claim_form', response.context)
        self.assertFalse(response.context['has_pending_claim'])

    def test_has_pending_claim_is_true_with_pending_claim(self):
        """has_pending_claim is True when the user has a pending claim on the item."""
        Claim.objects.create(item=self.found_item, claimant=self.claimant, message='É minha')
        response = self.get_detail(self.found_item, 'claimant')
        self.assertTrue(response.context['has_pending_claim'])

    def test_has_pending_claim_ignores_rejected_claims(self):
        """A rejected claim does not count as pending."""
        Claim.objects.create(
            item=self.found_item, claimant=self.claimant, message='É minha', status=Claim.Status.REJECTED
        )
        response = self.get_detail(self.found_item, 'claimant')
        self.assertFalse(response.context['has_pending_claim'])

    def test_author_of_found_item_sees_received_claims(self):
        """The author of a found item gets the list of claims received on it."""
        claim = Claim.objects.create(item=self.found_item, claimant=self.claimant, message='É minha')
        response = self.get_detail(self.found_item, 'finder')
        self.assertEqual(list(response.context['received_claims']), [claim])

    def test_other_user_does_not_see_received_claims(self):
        """Users other than the author do not get the received claims."""
        Claim.objects.create(item=self.found_item, claimant=self.claimant, message='É minha')
        response = self.get_detail(self.found_item, 'claimant')
        self.assertNotIn('received_claims', response.context)

    def test_author_of_lost_item_does_not_get_received_claims(self):
        """Lost items cannot be claimed, so their author gets no received claims."""
        response = self.get_detail(self.lost_item, 'finder')
        self.assertNotIn('received_claims', response.context)
