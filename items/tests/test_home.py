from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from items.models import Item

User = get_user_model()


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student_home',
            email='student_home@ufmg.br',
            password='password123',
        )

    def _create_item(self, title, status=Item.Status.OPEN):
        return Item.objects.create(
            author=self.user,
            title=title,
            description=f'Descrição de {title}',
            kind=Item.Kind.LOST,
            category=Item.Category.OTHER,
            location=Item.Location.ICEX,
            occurred_on=timezone.now().date(),
            status=status,
        )

    def test_home_displays_only_open_items(self):
        open_item = self._create_item('Carteira Aberta', status=Item.Status.OPEN)
        closed_item = self._create_item('Chave Resolvida', status=Item.Status.RESOLVED)

        response = self.client.get(reverse('home'))
        recent_items = list(response.context['recent_items'])

        self.assertEqual(response.status_code, 200)
        self.assertIn(open_item, recent_items)
        self.assertNotIn(closed_item, recent_items)

    def test_home_displays_at_most_eight_items(self):
        for i in range(10):
            self._create_item(f'Item {i}')

        response = self.client.get(reverse('home'))
        recent_items = list(response.context['recent_items'])

        self.assertEqual(len(recent_items), 8)

    def test_home_orders_items_from_newest_to_oldest(self):
        base_time = timezone.now()
        items = []
        for i in range(3):
            item = self._create_item(f'Item Cronológico {i}')
            Item.objects.filter(pk=item.pk).update(
                created_at=base_time + timedelta(minutes=i)
            )
            item.refresh_from_db()
            items.append(item)

        response = self.client.get(reverse('home'))
        recent_items = list(response.context['recent_items'])

        self.assertEqual(recent_items, [items[2], items[1], items[0]])
