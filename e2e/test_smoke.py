from playwright.sync_api import expect

from .base import E2ETestCase


class SmokeTests(E2ETestCase):
    def test_home_page_loads(self):
        """Checks that the live server and the browser are wired up."""
        self.page.goto(self.url('/'))
        expect(self.page).to_have_title('Início · Perdi e Achei')
        expect(self.page.get_by_role('heading', name='Perdeu ou achou algo no campus?')).to_be_visible()
