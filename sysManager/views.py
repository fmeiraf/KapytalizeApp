from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import ModelFormMixin
from portfolios import models
from . import forms

class CargasListView(LoginRequiredMixin, ListView, ModelFormMixin):
    model = models.PrecoAtivo
    form_class = forms.TipoAtivoForm
    template_name = 'sysManager/check_cargas.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        self.form = self.get_form(self.form_class)
        return ListView.get(self, request,*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(CargasListView, self).get_context_data(*args, **kwargs)
        context['form'] = self.form
        return context
