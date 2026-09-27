from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView

from .forms import ClaimForm, ItemForm
from .models import Claim, Item


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
        if self.request.user.is_authenticated:
            context['claim_form'] = ClaimForm()
            context['has_pending_claim'] = self.object.claims.filter(
                claimant=self.request.user, status=Claim.Status.PENDING
            ).exists()
        return context


class ClaimCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Claim
    form_class = ClaimForm
    success_message = 'Reivindicação enviada com sucesso!'
    # The form is embedded in the item detail page, not rendered on its own
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(Item, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.item.author_id == request.user.id:
            messages.error(request, 'Você não pode reivindicar um item que você mesmo cadastrou.')
            return redirect('item_detail', pk=self.item.pk)
        if self.item.status != Item.Status.OPEN:
            messages.error(request, 'Este item já foi resolvido e não pode mais ser reivindicado.')
            return redirect('item_detail', pk=self.item.pk)
        if Claim.objects.filter(item=self.item, claimant=request.user, status=Claim.Status.PENDING).exists():
            messages.error(request, 'Você já tem uma reivindicação pendente para este item.')
            return redirect('item_detail', pk=self.item.pk)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.item = self.item
        form.instance.claimant = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Não foi possível enviar a reivindicação. A mensagem não pode ficar vazia.')
        return redirect('item_detail', pk=self.item.pk)

    def get_success_url(self):
        return self.item.get_absolute_url()
