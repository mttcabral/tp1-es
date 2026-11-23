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
