from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from items.models import Claim, Item

from .forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        # Logged-in users have no reason to sign up again
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # CreateView saves the user; then log them in right away
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Bem-vindo(a), {self.object.username}! Cadastro realizado com sucesso.')
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_items'] = Item.objects.filter(author=self.request.user).annotate(
            pending_claims_count=Count('claims', filter=Q(claims__status=Claim.Status.PENDING))
        ).order_by('-created_at')
        
        context['my_claims'] = Claim.objects.filter(claimant=self.request.user).select_related('item').order_by('-created_at')
        return context
