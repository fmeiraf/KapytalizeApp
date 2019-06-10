from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import ModelFormMixin
from django_filters.views import FilterView
from portfolios import models
from django.db.models import Max

from . import forms

# class CargasListView(LoginRequiredMixin, ListView, ModelFormMixin):
#     model = models.PrecoAtivo
#     form_class = forms.TipoAtivoForm
#     template_name = 'sysManager/check_cargas.html'
#
#     def get(self, request, *args, **kwargs):
#         self.object = None
#         self.form = self.get_form(self.form_class)
#         return ListView.get(self, request,*args, **kwargs)
#
#     def get_context_data(self, *args, **kwargs):
#         context = super(CargasListView, self).get_context_data(*args, **kwargs)
#         context['form'] = self.form
#         return context

# class CargasListView(LoginRequiredMixin, FilterView):
#     model = models.PrecoAtivo
#     context_object_name = 'precos'
#     filter_class = forms.TipoAtivoFilter
#     template_name = 'sysManager/check_cargas.html'
#     paginate_by = 10

def CargasListView(request):
    form = forms.TipoAtivoFilter()
    precos = models.PrecoAtivo
    dateRef = precos.objects.all().order_by('-data')[0]
    lastdate = dateRef.data.date()


    try:
        filter = request.GET['tipo_ativo']
    except:
        filter = None
    print(filter)

    if filter != None:
        #qs = precos.objects.filter(cod_ativo__grupo_ativo__cod_grupo__exact=filter).order_by('-data', 'cod_ativo').distinct('data', 'cod_ativo')
        qs = precos.objects.raw('SELECT * FROM price JOIN ativo_detalhe USING(cod_ativo) WHERE grupo_ativo = {} AND cod_preco IN ( \
                                 SELECT MAX(cod_preco) FROM price GROUP BY cod_ativo )'.format(filter))
        #qs2 = precos.objects.filter(cod_ativo=4537).annotate(max_cod=Max('cod_preco')).values_list('max_cod')
        qs2 = precos.objects.filter(cod_ativo=4537).aggregate(Max('cod_preco'))

        print(qs2)
    else:
        qs = []

    return render(request, 'sysManager/check_cargas.html', { 'form' : form, 'qs' : qs, 'lastdate' : lastdate })
