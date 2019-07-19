from django.shortcuts import render
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db.models import Q
import datetime

from django import db
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
    context_object_name = 'portfolios'

    def get_queryset(self):
        return models.Portfolio.objects.filter(user=self.request.user).order_by('-data_criacao')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        user_portfolios = models.Portfolio.objects.filter(user=self.request.user).order_by('-data_criacao')
        aplicacao_byTipo_func = models.Aplicacao.customObjects.get_valor_byTipo

        aplica_preco = dict([(portfolio, aplicacao_byTipo_func(pk=portfolio.pk)) for portfolio in user_portfolios])

        valorTotalAplicado = 0
        valorTotalAtualizado = 0
        for port, aplics in aplica_preco.items():
            lista_ativos = models.Aplicacao.customObjects.get_ativos_detail(port.pk)
            for ativo, params in lista_ativos.items():
                valorTotalAplicado += params['valor_aplicado']
                ultimoPreco = models.PrecoAtivo.customObjects.get_last_prices_unity(ativo.cod_ativo)
                valorTotalAtualizado += float(params['quantidade']) * ultimoPreco

        ganho = round(((valorTotalAtualizado/valorTotalAplicado)-1),2)*100

        data['portfolios_completo'] = aplica_preco
        data['valorTotalAplicado'] = round(valorTotalAplicado)
        data['valorTotalAtualizado'] = round(valorTotalAtualizado)
        data['ganho'] = ganho

        return data


class PortfolioDetailView(LoginRequiredMixin, DetailView):
    model = models.Portfolio
    template_name = 'portfolios/portfolio_detail.html'

class PortfolioDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Portfolio
    success_url = reverse_lazy('portfolios:list')
    template_name = 'portfolios/portfolio_delete.html'
    context_object_name = 'portfolios'


class AtivoAutoComplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            qs = models.AtivoDetalhe.objects.none()

        qs = models.AtivoDetalhe.objects.all()

        tipoAtivo = self.forwarded.get('tipo_ativo', None)
        #pdb.set_trace()
        if tipoAtivo != '3':
            print('not 3')
            qs = qs.filter(grupo_ativo=tipoAtivo)
        else:
            print('its 3')
            qs = qs.filter(grupo_ativo=tipoAtivo).exclude(sigla_ativo__startswith='COMPRA-')

        if self.q:
            qs = qs.filter( Q(desc_ativo__icontains=self.q) |
                            Q(sigla_ativo__icontains=self.q) )

        return qs

    def get_result_label(self, item):
        tipoAtivo = self.forwarded.get('tipo_ativo', None)

        if tipoAtivo == '3':
            return '{}'.format(item.desc_ativo)
        else:
            return '{} - {}'.format(item.desc_ativo,item.sigla_ativo)

    def get_selected_result_label(self, item):
        tipoAtivo = self.forwarded.get('tipo_ativo', None)

        if tipoAtivo == 3:
            return '{}'.format(item.desc_ativo)
        else:
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
    return render(request, 'portfolios/manage_portfolio.html', {'formset': formset,
                                                                'portfolio':portfolio})

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

@login_required
def portfolio_resumo(request, pk):
    portfolio = get_object_or_404(models.Portfolio, pk=pk)
    aplicacoes = models.Aplicacao.customObjects.get_aplic_list(portfolio.pk)
    tiposAtivo = models.Aplicacao.customObjects.get_tipoAplicacao_list(portfolio.pk)

    # need : {ativo, ultpreco, ganhoValorizaçao, Rendas/Dividendos, GanhoPosDividendos}
    aplicsDetalhe = dict()
    contagem_ativos = []
    for aplic in aplicacoes:
        infoAtivo = dict()
        ##pegando ultimo preço
        infoAtivo['ultimoPreco'] = models.PrecoAtivo.customObjects.get_last_prices_unity(aplic.ativo.pk)
        infoAtivo['valorFinalAtualizado'] = infoAtivo['ultimoPreco'] * aplic.quantidade_aplicada
        infoAtivo['ganhoNominalPreco'] = infoAtivo['valorFinalAtualizado'] - aplic.valor_aplicado
        infoAtivo['ganhoPercPreco'] = round((((infoAtivo['valorFinalAtualizado'] / aplic.valor_aplicado) - 1)*100), 1)

        ##pegando proventos
        if aplic.ativo in contagem_ativos:
            infoAtivo['proventos'] = 0
            infoAtivo['ganhoNominalRendas'] = 0
            infoAtivo['ganhoPercRendas'] = 0
            infoAtivo['valorFinalAtualizadoRendas'] = infoAtivo['valorFinalAtualizado']
        else:
            proventosOficiais = models.Proventos.customObjects.get_proventos_detail_unity(aplic)
            if proventosOficiais == {}:
                infoAtivo['proventos'] = 0
                infoAtivo['ganhoNominalRendas'] = 0
                infoAtivo['ganhoPercRendas'] = 0
                infoAtivo['valorFinalAtualizadoRendas'] = infoAtivo['valorFinalAtualizado']
            else:
                proventosPagos = [ dados['valor'] * aplic.quantidade_aplicada for cod,dados in proventosOficiais.items() ]
                infoAtivo['proventos'] = sum(proventosPagos)
                infoAtivo['ganhoNominalRendas'] = (infoAtivo['valorFinalAtualizado'] + infoAtivo['proventos']) - aplic.valor_aplicado
                infoAtivo['ganhoPercRendas'] = round(((((infoAtivo['valorFinalAtualizado'] + infoAtivo['proventos']) / aplic.valor_aplicado) -1)*100),1)
                infoAtivo['valorFinalAtualizadoRendas'] = infoAtivo['valorFinalAtualizado'] + infoAtivo['proventos']

        contagem_ativos.append(aplic.ativo)

        aplicsDetalhe[aplic] = infoAtivo

    # Valor Aplicado + Ganho - por categoria
    valoresTipo = dict()
    for tipo in tiposAtivo:
        valorAplicado = [aplic.valor_aplicado for aplic,dados in aplicsDetalhe.items() if aplic.ativo.grupo_ativo.desc_grupo==tipo]
        valorAtualizado = [dados['valorFinalAtualizadoRendas'] for aplic,dados in aplicsDetalhe.items() if aplic.ativo.grupo_ativo.desc_grupo==tipo]
        ganhoNominal = [dados['ganhoNominalPreco'] for aplic,dados in aplicsDetalhe.items() if aplic.ativo.grupo_ativo.desc_grupo==tipo]
        provento = [dados['proventos'] for aplic,dados in aplicsDetalhe.items() if aplic.ativo.grupo_ativo.desc_grupo==tipo]
        valoresTipo[tipo] = { 'valorAplicado': sum(valorAplicado),
                              'valorAtualizado': sum(valorAtualizado),
                              'proventos': sum(provento),
                              'ganhoNominal': sum(ganhoNominal),
                              'ganhoFinal': sum(valorAtualizado)-sum(valorAplicado),
                              'GanhoPerc': round(((sum(valorAtualizado)/sum(valorAplicado)-1)*100),1),}

    # Valor Aplicado + Ganho - total Portfolio
    valoresTotais = dict()
    valoresTotaisAplicado = [value['valorAplicado'] for keys, value in valoresTipo.items()]
    valoresTotaisAtualizado = [value['valorAtualizado'] for keys, value in valoresTipo.items()]
    valoresTotaisGanhoNominal= [value['ganhoNominal'] for keys, value in valoresTipo.items()]
    valoresTotaisProventos= [value['proventos'] for keys, value in valoresTipo.items()]
    valoresTotaisGanhoFinal= [value['ganhoFinal'] for keys, value in valoresTipo.items()]


    valoresTotais['valorAplicado'] = sum(valoresTotaisAplicado)
    valoresTotais['valorAtualizado'] = sum(valoresTotaisAtualizado)
    valoresTotais['GanhoPerc'] = round((((valoresTotais['valorAtualizado'] / valoresTotais['valorAplicado']) - 1)*100),1)
    valoresTotais['ganhoNominal'] = sum(valoresTotaisGanhoNominal)
    valoresTotais['proventos'] = sum(valoresTotaisProventos)
    valoresTotais['ganhoFinal'] = sum(valoresTotaisGanhoFinal)

    print(valoresTotais)
    # Destaques do dia: valor ativo ontem vs valorHoje -> evolução


    return render(request, 'portfolios/resumo.html', { 'portfolio' : portfolio,
                                                       'tipoAtivo': tiposAtivo,
                                                       'aplicacoes' : aplicsDetalhe,
                                                       'dadosTipo' : valoresTipo,
                                                       'dadosTotais': valoresTotais} )
