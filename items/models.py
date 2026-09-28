from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Item(models.Model):
    """A lost or found object registered by a user."""

    class Kind(models.TextChoices):
        LOST = 'lost', 'Perdido'
        FOUND = 'found', 'Encontrado'

    class Category(models.TextChoices):
        ELECTRONICS = 'electronics', 'Eletrônicos'
        DOCUMENTS = 'documents', 'Documentos'
        KEYS = 'keys', 'Chaves'
        WALLETS_BAGS = 'wallets_bags', 'Carteiras e bolsas'
        CLOTHING = 'clothing', 'Roupas e acessórios'
        SCHOOL_SUPPLIES = 'school_supplies', 'Material escolar'
        BOTTLES = 'bottles', 'Garrafas e copos'
        OTHER = 'other', 'Outros'

    class Location(models.TextChoices):
        ICEX = 'icex', 'ICEx'
        CAD1 = 'cad1', 'CAD 1'
        CAD2 = 'cad2', 'CAD 2'
        CAD3 = 'cad3', 'CAD 3'
        ENGINEERING = 'engineering', 'Escola de Engenharia'
        CENTRAL_LIBRARY = 'central_library', 'Biblioteca Central'
        FAFICH = 'fafich', 'FAFICH'
        LETTERS = 'letters', 'Faculdade de Letras'
        RESTAURANT = 'restaurant', 'Restaurante Universitário'
        SERVICES_SQUARE = 'services_square', 'Praça de Serviços'
        SPORTS_CENTER = 'sports_center', 'Centro Esportivo'
        OTHER = 'other', 'Outro'

    class Period(models.TextChoices):
        MORNING = 'morning', 'Manhã'
        AFTERNOON = 'afternoon', 'Tarde'
        NIGHT = 'night', 'Noite'
        __empty__ = 'Não sei'

    class Status(models.TextChoices):
        OPEN = 'open', 'Aberto'
        RESOLVED = 'resolved', 'Resolvido'

    kind = models.CharField('tipo', max_length=10, choices=Kind.choices)
    title = models.CharField('título', max_length=100)
    description = models.TextField(
        'descrição', help_text='Descreva o item e o ponto exato onde foi perdido ou encontrado (sala, andar etc.).'
    )
    category = models.CharField('categoria', max_length=20, choices=Category.choices)
    location = models.CharField('local', max_length=20, choices=Location.choices)
    occurred_on = models.DateField('data do ocorrido', default=timezone.localdate)
    occurred_period = models.CharField('turno', max_length=10, choices=Period.choices, blank=True)
    photo = models.ImageField('foto', upload_to='items/', blank=True)
    status = models.CharField('status', max_length=10, choices=Status.choices, default=Status.OPEN)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items', verbose_name='autor'
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'item'
        verbose_name_plural = 'itens'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_kind_display()})'

    def get_absolute_url(self):
        return reverse('item_detail', args=[self.pk])


class Claim(models.Model):
    """A claim of ownership made by a user on an item."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        ACCEPTED = 'accepted', 'Aceita'
        REJECTED = 'rejected', 'Recusada'

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims', verbose_name='item')
    claimant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claims', verbose_name='reivindicante'
    )
    message = models.TextField('mensagem', help_text='Explique por que esse item é seu.')
    status = models.CharField('status', max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'reivindicação'
        verbose_name_plural = 'reivindicações'
        ordering = ['-created_at']

    def __str__(self):
        return f'Reivindicação de {self.claimant} em {self.item}'


class Comment(models.Model):
    """A comment left by a user on an item."""

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='comments', verbose_name='item')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', verbose_name='autor'
    )
    text = models.TextField('texto')
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'comentário'
        verbose_name_plural = 'comentários'
        ordering = ['created_at']

    def __str__(self):
        return f'Comentário de {self.author} em {self.item}'
