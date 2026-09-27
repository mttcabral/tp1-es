from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView

from .forms import CommentForm, ItemForm
from .models import Comment, Item


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.select_related('author')
        context['comment_form'] = CommentForm()
        return context


class CommentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Comment
    form_class = CommentForm
    success_message = 'Comentário adicionado com sucesso!'
    # The form is embedded in the item detail page, not rendered on its own
    http_method_names = ['post']

    def form_valid(self, form):
        form.instance.item = get_object_or_404(Item, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Não foi possível adicionar o comentário. O texto não pode ficar vazio.')
        return redirect('item_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return self.object.item.get_absolute_url()
