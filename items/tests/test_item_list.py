from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from items.models import Item

User = get_user_model()


class ItemListViewTests(TestCase):
    """Unit tests for ItemListView search, filtering, and pagination."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='student_list',
            email='student_list@ufmg.br',
            password='password123',
        )
        self.url = reverse('item_list')

    def _create_item(
        self,
        title,
        description='Descrição padrão',
        kind=Item.Kind.LOST,
        category=Item.Category.ELECTRONICS,
        location=Item.Location.ICEX,
        status=Item.Status.OPEN,
    ):
        return Item.objects.create(
            author=self.user,
            title=title,
            description=description,
            kind=kind,
            category=category,
            location=location,
            occurred_on=timezone.now().date(),
            status=status,
        )

    def test_search_by_title_case_insensitive(self):
        """Ensure query param q matches item title case-insensitively."""
        match = self._create_item(title='Garrafa Térmica Azul')
        other = self._create_item(title='Guarda-chuva')

        response = self.client.get(self.url, {'q': 'térmica'})
        items = list(response.context['items'])

        self.assertEqual(items, [match])
        self.assertNotIn(other, items)

    def test_search_by_description_case_insensitive(self):
        """Ensure query param q matches item description case-insensitively."""
        match = self._create_item(
            title='Mochila Preta',
            description='Contém um CADERNO de Engenharia de Software',
        )
        other = self._create_item(title='Guarda-chuva')

        response = self.client.get(self.url, {'q': 'caderno'})
        items = list(response.context['items'])

        self.assertEqual(items, [match])
        self.assertNotIn(other, items)

    def test_filter_by_kind(self):
        """Ensure kind filter returns only items with matching kind."""
        target = self._create_item(title='Fone Achado', kind=Item.Kind.FOUND)
        self._create_item(title='Fone Perdido', kind=Item.Kind.LOST)

        response = self.client.get(self.url, {'kind': Item.Kind.FOUND})
        self.assertEqual(list(response.context['items']), [target])

    def test_filter_by_category(self):
        """Ensure category filter returns only items with matching category."""
        target = self._create_item(title='Calculadora', category=Item.Category.ELECTRONICS)
        self._create_item(title='Livro', category=Item.Category.SCHOOL_SUPPLIES)

        response = self.client.get(self.url, {'category': Item.Category.ELECTRONICS})
        self.assertEqual(list(response.context['items']), [target])

    def test_filter_by_location(self):
        """Ensure location filter returns only items with matching location."""
        target = self._create_item(title='Chave', location=Item.Location.FAFICH)
        self._create_item(title='Carteira', location=Item.Location.ICEX)

        response = self.client.get(self.url, {'location': Item.Location.FAFICH})
        self.assertEqual(list(response.context['items']), [target])

    def test_filter_by_status(self):
        """Ensure status filter returns only items with matching status."""
        target = self._create_item(title='Item Aberto', status=Item.Status.OPEN)
        self._create_item(title='Item Resolvido', status=Item.Status.RESOLVED)

        response = self.client.get(self.url, {'status': Item.Status.OPEN})
        self.assertEqual(list(response.context['items']), [target])

    def test_combined_filters_with_search_query(self):
        """Ensure search query and all filter parameters work together."""
        target = self._create_item(
            title='Calculadora Científica',
            kind=Item.Kind.FOUND,
            category=Item.Category.ELECTRONICS,
            location=Item.Location.FAFICH,
            status=Item.Status.OPEN,
        )
        self._create_item(
            title='Calculadora Simples',
            kind=Item.Kind.LOST,
            category=Item.Category.ELECTRONICS,
            location=Item.Location.ICEX,
            status=Item.Status.RESOLVED,
        )

        params = {
            'q': 'calculadora',
            'kind': Item.Kind.FOUND,
            'category': Item.Category.ELECTRONICS,
            'location': Item.Location.FAFICH,
            'status': Item.Status.OPEN,
        }
        response = self.client.get(self.url, params)
        self.assertEqual(list(response.context['items']), [target])

    def test_invalid_filter_value_lists_all_items(self):
        """Ensure invalid filter choices do not crash and fall back to listing all items."""
        item1 = self._create_item(title='Item A', kind=Item.Kind.LOST)
        item2 = self._create_item(title='Item B', kind=Item.Kind.FOUND)

        response = self.client.get(self.url, {'kind': 'xyz'})
        items = list(response.context['items'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(item1, items)
        self.assertIn(item2, items)

    def test_pagination_and_filter_preservation_in_url(self):
        """Ensure page 2 holds the 13th item and preserves active filters in URL."""
        for i in range(13):
            self._create_item(
                title=f'Notebook {i}',
                kind=Item.Kind.LOST,
                category=Item.Category.ELECTRONICS,
            )

        res_page_1 = self.client.get(
            self.url,
            {
                'q': 'Notebook',
                'kind': Item.Kind.LOST,
                'category': Item.Category.ELECTRONICS,
            },
        )
        self.assertEqual(len(res_page_1.context['items']), 12)
        self.assertContains(
            res_page_1,
            f'href="?page=2&q=Notebook&kind={Item.Kind.LOST}&category={Item.Category.ELECTRONICS}"',
        )

        res_page_2 = self.client.get(
            self.url,
            {
                'page': 2,
                'q': 'Notebook',
                'kind': Item.Kind.LOST,
                'category': Item.Category.ELECTRONICS,
            },
        )
        self.assertEqual(res_page_2.status_code, 200)
        self.assertEqual(len(res_page_2.context['items']), 1)
