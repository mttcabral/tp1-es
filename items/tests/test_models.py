from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from items.models import Claim, Comment, Item

User = get_user_model()


class ModelMethodTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('ana', password='password123')
        cls.other = User.objects.create_user('bia', password='password123')
        cls.item = Item.objects.create(
            author=cls.owner,
            kind=Item.Kind.FOUND,
            title='Carteira preta',
            description='Achada perto do RU.',
            category=Item.Category.WALLETS_BAGS,
            location=Item.Location.RESTAURANT,
        )

    def test_item_str_shows_title_and_kind_label(self):
        """The item is shown by its title plus the Portuguese label of its kind."""
        self.assertEqual(str(self.item), 'Carteira preta (Encontrado)')

    def test_item_absolute_url_is_the_detail_page(self):
        """get_absolute_url points to the item detail page (used by redirects)."""
        self.assertEqual(self.item.get_absolute_url(), reverse('item_detail', args=[self.item.pk]))

    def test_claim_str_shows_claimant_and_item(self):
        claim = Claim.objects.create(item=self.item, claimant=self.other, message='É minha!')
        self.assertEqual(str(claim), 'Reivindicação de bia em Carteira preta (Encontrado)')

    def test_comment_str_shows_author_and_item(self):
        comment = Comment.objects.create(item=self.item, author=self.other, text='Vi uma igual.')
        self.assertEqual(str(comment), 'Comentário de bia em Carteira preta (Encontrado)')
