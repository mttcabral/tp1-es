import datetime

from django.test import TestCase
from django.utils import timezone

from items.forms import ItemForm
from items.models import Item


def item_data(**overrides):
    data = {
        'kind': Item.Kind.FOUND,
        'title': 'Guarda-chuva vermelho',
        'description': 'Esquecido no corredor do 3º andar da FAFICH.',
        'category': Item.Category.CLOTHING,
        'location': Item.Location.FAFICH,
        'occurred_on': timezone.localdate().isoformat(),
        'occurred_period': Item.Period.AFTERNOON,
    }
    data.update(overrides)
    return data


class ItemFormTests(TestCase):
    def test_rejects_date_in_the_future(self):
        """An item cannot be lost or found on a day that has not happened yet."""
        tomorrow = timezone.localdate() + datetime.timedelta(days=1)
        form = ItemForm(data=item_data(occurred_on=tomorrow.isoformat()))
        self.assertFalse(form.is_valid())
        self.assertIn('A data não pode estar no futuro.', form.errors['occurred_on'])

    def test_accepts_today(self):
        """Today is the latest valid date."""
        form = ItemForm(data=item_data())
        self.assertTrue(form.is_valid(), form.errors)


class BootstrapFormMixinTests(TestCase):
    def test_select_gets_form_select_and_other_fields_form_control(self):
        """Bootstrap styles <select> with form-select; every other input uses form-control."""
        fields = ItemForm().fields
        for name in ('kind', 'category', 'location', 'occurred_period'):
            self.assertEqual(fields[name].widget.attrs['class'], 'form-select', name)
        for name in ('title', 'description', 'occurred_on', 'photo'):
            self.assertEqual(fields[name].widget.attrs['class'], 'form-control', name)

    def test_field_with_error_gets_is_invalid(self):
        """After validation, fields with errors are marked is-invalid; valid ones are not."""
        form = ItemForm(data=item_data(title=''))
        self.assertFalse(form.is_valid())
        self.assertIn('is-invalid', form.fields['title'].widget.attrs['class'])
        self.assertNotIn('is-invalid', form.fields['description'].widget.attrs['class'])
