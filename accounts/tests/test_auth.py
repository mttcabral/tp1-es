from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from accounts.forms import SignUpForm

User = get_user_model()
PASSWORD = 'Perdi&Achei2026'


def signup_data(**overrides):
    data = {'username': 'ana', 'email': 'ana@example.com', 'password1': PASSWORD, 'password2': PASSWORD}
    data.update(overrides)
    return data


class SignUpFormTests(TestCase):
    def test_rejects_email_already_used_with_different_case(self):
        """E-mail is unique regardless of case: Ana@x.com clashes with ana@x.com."""
        User.objects.create_user('existing', 'ana@example.com', PASSWORD)
        form = SignUpForm(data=signup_data(username='other', email='Ana@Example.com'))
        self.assertFalse(form.is_valid())
        self.assertIn('Já existe um usuário com este e-mail.', form.errors['email'])

    def test_saves_email_in_lowercase(self):
        """The e-mail is normalized to lowercase before being saved."""
        form = SignUpForm(data=signup_data(email='Ana@Example.COM'))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().email, 'ana@example.com')


class SignUpViewTests(TestCase):
    url = reverse('signup')

    def test_valid_signup_creates_user_logs_in_and_redirects_home(self):
        """A valid sign-up creates the user, starts the session and greets them on the home page."""
        response = self.client.post(self.url, signup_data())
        self.assertRedirects(response, reverse('home'))
        user = User.objects.get(username='ana')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)
        messages = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertIn('Bem-vindo(a), ana! Cadastro realizado com sucesso.', messages)

    def test_logged_in_user_is_redirected_away_from_signup(self):
        """Someone already logged in has no reason to sign up again."""
        User.objects.create_user('ana', 'ana@example.com', PASSWORD)
        self.client.login(username='ana', password=PASSWORD)
        self.assertRedirects(self.client.get(self.url), reverse('home'))


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ana', 'ana@example.com', PASSWORD)

    def test_wrong_password_shows_error_and_does_not_log_in(self):
        """A wrong password re-renders the form with an error and no session is created."""
        response = self.client.post(reverse('login'), {'username': 'ana', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].non_field_errors())
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logged_in_user_is_redirected_away_from_login(self):
        """The login page sends users who are already logged in to the home page."""
        self.client.login(username='ana', password=PASSWORD)
        self.assertRedirects(self.client.get(reverse('login')), reverse('home'))

    def test_logout_by_post_ends_the_session(self):
        """Logout is a POST (Django 5) and clears the session."""
        self.client.login(username='ana', password=PASSWORD)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)
