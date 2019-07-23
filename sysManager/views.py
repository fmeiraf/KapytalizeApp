from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import ModelFormMixin
from django_filters.views import FilterView
from portfolios import models
from django.db.models import Max
from django.contrib.admin.views.decorators import staff_member_required

from . import forms

@staff_member_required
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

        qs = precos.objects.raw('SELECT * FROM price JOIN ativo_detalhe USING(cod_ativo) WHERE grupo_ativo = {} AND cod_preco IN ( \
                                 SELECT MAX(cod_preco) FROM price GROUP BY cod_ativo )'.format(filter))
    else:
        qs = []

    return render(request, 'sysManager/check_cargas.html', { 'form' : form, 'qs' : qs, 'lastdate' : lastdate })
