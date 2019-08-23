from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django import forms
from . import models
import pdb
from dal import autocomplete


class DateInput (forms.DateInput):
    input_type='date'

class PortfolioCreationForm(ModelForm):
    class Meta:
        model = models.Portfolio
        fields = ['nome']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PortfolioCreationForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PortfolioCreationForm, self).clean()
        user_portfolios = [port.nome for port in models.Portfolio.objects.filter(user=self.request.user)]
        if cleaned_data.get('nome') in user_portfolios:
            raise ValidationError("Esse nome de Portfolio já existe. Por favor, escolha um outro nome.")


class AplicacaoCreationForm(ModelForm):
    tipo_ativo = forms.ModelChoiceField(queryset=models.GrupoAtivo.objects.exclude(cod_grupo=6))

    class Meta:
        model = models.Aplicacao
        fields = ['tipo_ativo','ativo', 'data_aplicacao', 'preco_entrada', 'valor_aplicado', 'taxa_entrada', ]
        widgets = {
                'ativo': autocomplete.ModelSelect2(url='portfolios:ativo-autocomplete',
                                                   forward=['tipo_ativo']),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ativo'].queryset = models.AtivoDetalhe.objects.none()


        tipo_field = self.prefix + '-tipo_ativo'
        #pdb.set_trace()
        if tipo_field in self.data :
            try:
                tipoAtivo = self.data.get(tipo_field)
                self.fields['ativo'].queryset = models.AtivoDetalhe.objects.filter(grupo_ativo=tipoAtivo).order_by('desc_ativo')
            except(ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['tipo_ativo'].initial = self.instance.ativo.grupo_ativo
            self.fields['ativo'].queryset = models.AtivoDetalhe.objects.filter(grupo_ativo=self.instance.ativo.grupo_ativo).order_by('desc_ativo')
