from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, DetailView, ListView

from .forms import ItemFilterForm, ItemForm
from .models import Item


class ItemCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Item
    form_class = ItemForm
    success_message = 'Item cadastrado com sucesso!'

    def form_valid(self, form):
        # The author is the logged-in user, never a form field
        form.instance.author = self.request.user
        return super().form_valid(form)


class ItemDetailView(DetailView):
    # select_related fetches the author in the same query
    queryset = Item.objects.select_related('author')

class ItemListView(ListView):
    """Lists items with search and filtering capabilities."""
    model = Item
    template_name = 'items/item_list.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        queryset = Item.objects.select_related('author').order_by('-created_at')
        form = ItemFilterForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            if q:
                queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
            kind = form.cleaned_data.get('kind')
            if kind:
                queryset = queryset.filter(kind=kind)
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            location = form.cleaned_data.get('location')
            if location:
                queryset = queryset.filter(location=location)
            status = form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ItemFilterForm(self.request.GET)
        return context