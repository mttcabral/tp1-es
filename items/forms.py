from django import forms
from django.utils import timezone

from config.forms import BootstrapFormMixin

from .models import Item


class ItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Item
        # status and author are not filled in by the user
        fields = ('kind', 'title', 'description', 'category', 'location', 'occurred_on', 'occurred_period', 'photo')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            # type=date needs the ISO format, not the pt-BR one (dd/mm/yyyy)
            'occurred_on': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def clean_occurred_on(self):
        occurred_on = self.cleaned_data['occurred_on']
        if occurred_on > timezone.localdate():
            raise forms.ValidationError('A data não pode estar no futuro.')
        return occurred_on
class ItemFilterForm(BootstrapFormMixin, forms.Form):
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Título ou descrição...'}),
    )
    kind = forms.ChoiceField(
        label='Tipo',
        required=False,
        choices=[('', 'Todos os tipos')] + list(Item.Kind.choices),
    )
    category = forms.ChoiceField(
        label='Categoria',
        required=False,
        choices=[('', 'Todas as categorias')] + list(Item.Category.choices),
    )
    location = forms.ChoiceField(
        label='Local',
        required=False,
        choices=[('', 'Todos os locais')] + list(Item.Location.choices),
    )
    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[('', 'Todos os status')] + list(Item.Status.choices),
    )