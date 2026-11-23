from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from items.models import Item

from .base import E2ETestCase

User = get_user_model()


class CommentAndClaimTests(E2ETestCase):
    def setUp(self):
        super().setUp()
        finder = User.objects.create_user(username='finder', password='password123')
        User.objects.create_user(username='claimant', password='password123')
        self.item = Item.objects.create(
            author=finder,
            kind=Item.Kind.FOUND,
            title='Mochila preta',
            description='Encontrada no 2º andar do CAD 1',
            category=Item.Category.WALLETS_BAGS,
            location=Item.Location.CAD1,
        )

    def test_user_comments_and_claims_found_item(self):
        """User B logs in, comments on A's found item and claims it, then sees the pending notice."""
        self.login('claimant', 'password123')
        self.page.goto(self.url(self.item.get_absolute_url()))
        expect(self.page.get_by_role('heading', name='Mochila preta')).to_be_visible()

        self.page.get_by_label('Texto').fill('Acho que é a minha, tem um chaveiro de gato')
        self.page.get_by_role('button', name='Comentar').click()
        expect(self.page.get_by_text('Comentário adicionado com sucesso!')).to_be_visible()
        expect(self.page.locator('#comments')).to_contain_text('Acho que é a minha, tem um chaveiro de gato')

        self.page.get_by_label('Mensagem').fill('Dentro tem um caderno com meu nome')
        self.page.get_by_role('button', name='Isso é meu').click()
        expect(self.page.get_by_text('Reivindicação enviada com sucesso!')).to_be_visible()
        expect(self.page.locator('#claim')).to_contain_text('Você já enviou uma reivindicação para este item.')
