from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from . import forms


class SignUp(CreateView):
    form_class = forms.UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

class Logged(TemplateView):
    template_name = 'portfolios/portfolio_list.html'

class SuaConta(TemplateView):
    template_name = 'accounts/sua_conta.html'
