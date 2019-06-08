from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from collections import defaultdict

import pdb
from dal import autocomplete
from . import forms, models
from django.contrib.auth import get_user_model
User = get_user_model()

# --------------------- Portfolio creation and insertion -----------------------------------

class PortfolioCreate(LoginRequiredMixin, CreateView):
    model = models.Portfolio
    template_name = 'portfolios/portfolio_create_form.html'
    form_class = forms.PortfolioCreationForm
    success_url = '/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

class PortfolioListView(LoginRequiredMixin, ListView):
    model = models.Portfolio
    template_name = 'portfolios/portfolio_list.html'

    def get_queryset(self):
        return models.Portfolio.objects.filter(user=self.request.user).order_by('-data_criacao')

class PortfolioDetailView(LoginRequiredMixin, DetailView):
    model = models.Portfolio
    template_name = 'portfolios/portfolio_detail.html'

class AtivoAutoComplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            qs = models.AtivoDetalhe.objects.none()

        qs = models.AtivoDetalhe.objects.all()

        tipoAtivo = self.forwarded.get('tipo_ativo', None)
        if tipoAtivo:
            qs = qs.filter(grupo_ativo=tipoAtivo)

        if self.q:
            qs = qs.filter( Q(desc_ativo__istartswith=self.q) |
                            Q(sigla_ativo__istartswith=self.q) )

        return qs

    def get_result_label(self, item):
        return '{} - {}'.format(item.desc_ativo,item.sigla_ativo)

    def get_selected_result_label(self, item):
        return '{} - {}'.format(item.desc_ativo,item.sigla_ativo)

@login_required
def manage_portfolios(request, pk):
    portfolio = models.Portfolio.objects.get(pk=pk)
    PortfolioInlineFormset = inlineformset_factory( models.Portfolio, models.Aplicacao, fk_name='portfolio',
                                                    form= forms.AplicacaoCreationForm,
                                                    extra=1, can_delete=True )
    if request.method =='POST':
        formset = PortfolioInlineFormset(request.POST, request.FILES, instance=portfolio)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(portfolio.get_absolute_url())
    else:
        formset = PortfolioInlineFormset(instance=portfolio)
    return render(request, 'portfolios/manage_portfolio.html', {'formset':formset})

# --------------------- Portfolio visualization -----------------------------------

@login_required
def rentabilidade_portofolio(request, pk):
    portfolio = get_object_or_404(models.Portfolio, pk=pk)
    aplicacoes = models.Aplicacao.objects.filter(portfolio=portfolio.pk)

    aplica_preco = dict([(aplic, models.PrecoAtivo.objects.filter(cod_ativo=aplic.ativo.pk).last()) for aplic in aplicacoes])

    sectionChecker = [aplic.ativo.grupo_ativo.desc_grupo for aplic in aplicacoes]



    return render(request, 'portfolios/rentabilidade_portfolio.html', { 'portfolio' : portfolio,
                                                                        'aplicacoes' : aplica_preco,
                                                                        'sections' : sectionChecker} )
