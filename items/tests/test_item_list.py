from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from items.models import Item

User = get_user_model()


class ItemListViewTests(TestCase):
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

    def test_search_by_title_and_description_case_insensitive(self):
        item_title = self._create_item(title='Garrafa Térmica Azul')
        item_desc = self._create_item(
            title='Mochila Preta',
            description='Contém um CADERNO de Engenharia de Software',
        )
        item_other = self._create_item(title='Guarda-chuva')

        res_title = self.client.get(self.url, {'q': 'térmica'})
        self.assertEqual(list(res_title.context['items']), [item_title])

        res_desc = self.client.get(self.url, {'q': 'caderno'})
        self.assertEqual(list(res_desc.context['items']), [item_desc])
        self.assertNotIn(item_other, res_desc.context['items'])

    def test_individual_and_combined_filters(self):
        target = self._create_item(
            title='Calculadora Científica',
            kind=Item.Kind.FOUND,
            category=Item.Category.ELECTRONICS,
            location=Item.Location.FAFICH,
            status=Item.Status.OPEN,
        )
        other = self._create_item(
            title='Livro de Cálculo',
            kind=Item.Kind.LOST,
            category=Item.Category.SCHOOL_SUPPLIES,
            location=Item.Location.ICEX,
            status=Item.Status.RESOLVED,
        )

        # Single filters
        self.assertEqual(
            list(self.client.get(self.url, {'kind': Item.Kind.FOUND}).context['items']),
            [target],
        )
        self.assertEqual(
            list(
                self.client.get(
                    self.url, {'category': Item.Category.ELECTRONICS}
                ).context['items']
            ),
            [target],
        )
        self.assertEqual(
            list(
                self.client.get(
                    self.url, {'location': Item.Location.FAFICH}
                ).context['items']
            ),
            [target],
        )
        self.assertEqual(
            list(
                self.client.get(
                    self.url, {'status': Item.Status.OPEN}
                ).context['items']
            ),
            [target],
        )

        # Combined filters with search query
        combined_params = {
            'q': 'calculadora',
            'kind': Item.Kind.FOUND,
            'category': Item.Category.ELECTRONICS,
            'location': Item.Location.FAFICH,
            'status': Item.Status.OPEN,
        }
        response = self.client.get(self.url, combined_params)
        self.assertEqual(list(response.context['items']), [target])
        self.assertNotIn(other, response.context['items'])

    def test_invalid_filter_value_does_not_crash_and_lists_all(self):
        # Current behavior: when filter form validation fails due to an invalid
        # choice (e.g., ?kind=xyz), no filters are applied and all items are listed.
        item1 = self._create_item(title='Item A', kind=Item.Kind.LOST)
        item2 = self._create_item(title='Item B', kind=Item.Kind.FOUND)

        response = self.client.get(self.url, {'kind': 'xyz'})
        items = list(response.context['items'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(item1, items)
        self.assertIn(item2, items)

    def test_pagination_and_filter_preservation_in_url(self):
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
            f'href="?page=2&amp;q=Notebook&amp;kind={Item.Kind.LOST}&amp;category={Item.Category.ELECTRONICS}',
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
