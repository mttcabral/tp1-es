from django import forms

from config.forms import BootstrapFormMixin

from .models import Item


class ItemForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Item
        # status and author are not filled in by the user
        fields = ('kind', 'title', 'description', 'category', 'location', 'photo')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
