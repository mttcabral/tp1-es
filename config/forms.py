from django import forms


class BootstrapFormMixin:
    """Adds Bootstrap classes to every field widget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # Bootstrap styles <select> with form-select instead of form-control
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def full_clean(self):
        # Runs validation, then marks fields with errors as invalid
        super().full_clean()
        for name in self.errors:
            if name in self.fields:
                self.fields[name].widget.attrs['class'] += ' is-invalid'
