from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from e2e.base import E2ETestCase
from items.models import Item

User = get_user_model()


class SearchAndFilterE2ETests(E2ETestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username='e2e_user',
            email='e2e_user@ufmg.br',
            password='password123',
        )

    def test_search_and_category_filter_displays_expected_card(self):
        Item.objects.create(
            author=self.user,
            title='Fone Bluetooth JBL',
            description='Achado perto da cantina',
            kind=Item.Kind.FOUND,
            category=Item.Category.ELECTRONICS,
            location=Item.Location.ICEX,
            occurred_on=timezone.now().date(),
        )
        Item.objects.create(
            author=self.user,
            title='Fone com Fio Simples',
            description='Perdido na biblioteca',
            kind=Item.Kind.LOST,
            category=Item.Category.OTHER,
            location=Item.Location.CENTRAL_LIBRARY,
            occurred_on=timezone.now().date(),
        )
        Item.objects.create(
            author=self.user,
            title='Caderno de Algoritmos',
            description='Capa azul',
            kind=Item.Kind.LOST,
            category=Item.Category.SCHOOL_SUPPLIES,
            location=Item.Location.ICEX,
            occurred_on=timezone.now().date(),
        )

        self.page.goto(self.url(reverse('item_list')))
        self.page.fill('input[name="q"]', 'Fone')
        self.page.select_option('select[name="category"]', Item.Category.ELECTRONICS)
        self.page.click('button[type="submit"]')

        content = self.page.content()
        self.assertIn('Fone Bluetooth JBL', content)
        self.assertNotIn('Fone com Fio Simples', content)
        self.assertNotIn('Caderno de Algoritmos', content)
