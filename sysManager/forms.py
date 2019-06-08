from django.forms import ModelForm
from portfolios import models

class TipoAtivoForm(ModelForm):
    class Meta:
        model = models.GrupoAtivo
        fields = ['desc_grupo']
