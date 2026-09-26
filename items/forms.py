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
