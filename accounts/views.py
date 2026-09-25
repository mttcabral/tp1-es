from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # CreateView saves the user; then log them in right away
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f'Bem-vindo(a), {self.object.username}! Cadastro realizado com sucesso.')
        return response
