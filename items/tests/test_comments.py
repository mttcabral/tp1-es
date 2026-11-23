from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from items.models import Comment

from .helpers import make_item

User = get_user_model()


class CommentCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner', password='password123')
        cls.visitor = User.objects.create_user(username='visitor', password='password123')
        cls.item = make_item(cls.owner)
        cls.url = reverse('comment_create', args=[cls.item.pk])

    def setUp(self):
        self.client.login(username='visitor', password='password123')

    def test_anonymous_user_is_redirected_to_login(self):
        """A visitor who is not logged in is sent to the login page and no comment is saved."""
        self.client.logout()
        response = self.client.post(self.url, {'text': 'Vi uma parecida no RU'})
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")
        self.assertFalse(Comment.objects.exists())

    def test_valid_comment_is_saved_with_author_and_item(self):
        """A valid POST saves the comment for the logged-in user and the item, then goes back to the item page."""
        response = self.client.post(self.url, {'text': 'Vi uma parecida no RU'})
        self.assertRedirects(response, self.item.get_absolute_url())
        comment = Comment.objects.get()
        self.assertEqual(comment.text, 'Vi uma parecida no RU')
        self.assertEqual(comment.author, self.visitor)
        self.assertEqual(comment.item, self.item)

    def test_empty_text_shows_error_and_saves_nothing(self):
        """An empty text is rejected with an error message and no comment is saved."""
        response = self.client.post(self.url, {'text': ''})
        self.assertRedirects(response, self.item.get_absolute_url())
        self.assertFalse(Comment.objects.exists())
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertIn('Não foi possível adicionar o comentário. O texto não pode ficar vazio.', messages)

    def test_whitespace_only_text_is_treated_as_empty(self):
        """A text made only of spaces counts as empty: it is rejected and no comment is saved."""
        response = self.client.post(self.url, {'text': '   '})
        self.assertRedirects(response, self.item.get_absolute_url())
        self.assertFalse(Comment.objects.exists())

    def test_nonexistent_item_returns_404(self):
        """Commenting on an item that does not exist returns 404."""
        response = self.client.post(reverse('comment_create', args=[9999]), {'text': 'Oi'})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Comment.objects.exists())

    def test_get_is_not_allowed(self):
        """The comment form lives on the item page, so a GET to its URL returns 405."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
