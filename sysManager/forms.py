from portfolios import models
from django import forms
import django_filters

# class TipoAtivoFilter(django_filters.FilterSet):
#     desc_grupo = django_filters.CharFilter(field_name='desc_grupo', method=None)
#     class Meta:
#         model = models.GrupoAtivo
#         fields = ['desc_grupo']
#
#         def last_date_filter(self, queryset, name, value):
#             return queryset.filter().lastest('data')


class TipoAtivoFilter(forms.Form):
    tipo_ativo = forms.ModelChoiceField(queryset=models.GrupoAtivo.objects.all())
