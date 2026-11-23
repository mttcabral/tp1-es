import datetime
import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from items.forms import ItemForm
from items.models import Item

User = get_user_model()


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


def image_file(name='foto.jpg'):
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, 'JPEG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')


class ItemCreateViewTests(TestCase):
    url = reverse('item_create')

    def setUp(self):
        self.user = User.objects.create_user('ana', 'ana@example.com', 'password123')

    def test_visitor_is_redirected_to_login(self):
        """Only logged-in users can register items."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")

    def test_valid_post_saves_logged_user_as_author_with_open_status(self):
        """The author comes from the session (never from the form) and new items start open."""
        self.client.login(username='ana', password='password123')
        response = self.client.post(self.url, item_data())
        item = Item.objects.get()
        self.assertRedirects(response, item.get_absolute_url())
        self.assertEqual(item.author, self.user)
        self.assertEqual(item.status, Item.Status.OPEN)
        self.assertIn('Item cadastrado com sucesso!', [str(m) for m in get_messages(response.wsgi_request)])

    def test_photo_upload_is_saved(self):
        """An uploaded image is stored under media/items/ and linked to the item."""
        media_root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, media_root)
        self.client.login(username='ana', password='password123')
        with override_settings(MEDIA_ROOT=media_root):
            self.client.post(self.url, {**item_data(), 'photo': image_file()})
            item = Item.objects.get()
            self.assertTrue(item.photo.name.startswith('items/'))
            self.assertTrue(item.photo.storage.exists(item.photo.name))
