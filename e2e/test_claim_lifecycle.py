from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from items.models import Claim, Item

from .base import E2ETestCase

User = get_user_model()


class ClaimLifecycleTests(E2ETestCase):
    def setUp(self):
        super().setUp()
        finder = User.objects.create_user(username='finder', password='password123')
        claimant = User.objects.create_user(username='claimant', password='password123')
        self.item = Item.objects.create(
            author=finder,
            kind=Item.Kind.FOUND,
            title='Garrafa azul',
            description='Encontrada na Biblioteca Central',
            category=Item.Category.BOTTLES,
            location=Item.Location.CENTRAL_LIBRARY,
        )
        Claim.objects.create(
            item=self.item,
            claimant=claimant,
            message='Tem um adesivo da UFMG na tampa',
        )

    def test_owner_accepts_claim_and_claimant_sees_accepted_in_dashboard(self):
        """Owner logs in, accepts the claim and sees the item resolved; claimant logs in and sees Accepted on the dashboard."""
        self.login('finder', 'password123')
        self.page.goto(self.url(self.item.get_absolute_url()))
        expect(self.page.get_by_role('heading', name='Garrafa azul')).to_be_visible()
        expect(self.page.locator('#received-claims')).to_contain_text('Tem um adesivo da UFMG na tampa')

        self.page.get_by_role('button', name='Aceitar').click()
        expect(self.page.get_by_text('Reivindicação aceita com sucesso!')).to_be_visible()
        expect(self.page.locator('#item-info')).to_contain_text('Resolvido')
        expect(self.page.locator('#received-claims')).to_contain_text('Aceita')

        self.page.get_by_role('button', name='Sair').click()
        expect(self.page.get_by_role('navigation')).to_contain_text('Entrar')

        self.login('claimant', 'password123')
        self.page.get_by_role('navigation').get_by_role('link', name='Meu painel').click()
        expect(self.page.get_by_role('heading', name='Meu painel')).to_be_visible()
        claims_section = self.page.locator('section', has_text='Minhas reivindicações')
        expect(claims_section).to_contain_text('Garrafa azul')
        expect(claims_section).to_contain_text('Aceita')
