import re

from django.utils import timezone
from playwright.sync_api import expect

from .base import E2ETestCase


class SignUpAndItemTests(E2ETestCase):
    def test_visitor_signs_up_and_registers_an_item(self):
        """A visitor creates an account from the home page, is logged in and registers a found item."""
        self.page.goto(self.url('/'))
        self.page.get_by_role('navigation').get_by_role('link', name='Cadastrar', exact=True).click()

        self.page.get_by_label('Usuário').fill('davi')
        self.page.get_by_label('E-mail').fill('davi@example.com')
        self.page.get_by_label('Senha', exact=True).fill('Perdi&Achei2026')
        self.page.get_by_label('Confirmação de senha').fill('Perdi&Achei2026')
        self.page.get_by_role('button', name='Cadastrar').click()
        expect(self.page.get_by_text('Bem-vindo(a), davi! Cadastro realizado com sucesso.')).to_be_visible()
        expect(self.page.get_by_role('navigation')).to_contain_text('Olá, davi')

        self.page.get_by_role('navigation').get_by_role('link', name='Cadastrar item').click()
        self.page.get_by_label('Tipo').select_option(label='Encontrado')
        self.page.get_by_label('Título').fill('Guarda-chuva vermelho')
        self.page.get_by_label('Descrição').fill('Esquecido no corredor do 3º andar da FAFICH.')
        self.page.get_by_label('Categoria').select_option(label='Roupas e acessórios')
        self.page.get_by_label('Local').select_option(label='FAFICH')
        self.page.get_by_label('Data do ocorrido').fill(timezone.localdate().isoformat())
        self.page.get_by_label('Turno').select_option(label='Tarde')
        self.page.get_by_role('button', name='Cadastrar').click()

        expect(self.page.get_by_text('Item cadastrado com sucesso!')).to_be_visible()
        expect(self.page.get_by_role('heading', name='Guarda-chuva vermelho')).to_be_visible()
        expect(self.page).to_have_url(re.compile(r'/items/\d+/$'))
