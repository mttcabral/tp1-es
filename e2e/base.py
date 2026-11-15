import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from playwright.sync_api import sync_playwright

# Playwright's sync API runs an event loop; without this flag Django
# refuses database access from the test thread (SynchronousOnlyOperation)
os.environ.setdefault('DJANGO_ALLOW_ASYNC_UNSAFE', 'true')


@tag('e2e')
class E2ETestCase(StaticLiveServerTestCase):
    """Base class for end-to-end tests: a live server plus a Chromium browser.

    Run with HEADED=1 to watch the browser (slowed down for presentations).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        headed = os.environ.get('HEADED') == '1'
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=not headed, slow_mo=500 if headed else 0)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        # A fresh context per test: no cookies or session shared between tests
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def url(self, path):
        return f'{self.live_server_url}{path}'

    def login(self, username, password):
        """Logs in through the real login form."""
        self.page.goto(self.url('/accounts/login/'))
        self.page.get_by_label('Usuário').fill(username)
        self.page.get_by_label('Senha').fill(password)
        self.page.get_by_role('button', name='Entrar').click()
