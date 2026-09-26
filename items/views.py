from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, DetailView, ListView

from .forms import ItemForm
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
class HomeView(ListView):
    """Displays the most recent open lost and found items on the home page."""
    model = Item
    template_name = 'home.html'
    context_object_name = 'recent_items'

    def get_queryset(self):
        return Item.objects.filter(status=Item.Status.OPEN).select_related('author').order_by('-created_at')[:8]