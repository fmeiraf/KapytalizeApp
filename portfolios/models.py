from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

# ---- UnManaged models - Created outside Django ----

class AtivoDetalhe(models.Model):
    cod_ativo = models.AutoField(primary_key=True)
    desc_ativo = models.CharField(max_length=250)
    sigla_ativo = models.CharField(unique=True, max_length=250)
    data_inserido = models.DateTimeField(blank=True, null=True)
    grupo_ativo = models.ForeignKey('GrupoAtivo', models.DO_NOTHING, db_column='grupo_ativo')

    def __str__(self):
        return self.desc_ativo

    class Meta:
        managed = False
        db_table = 'ativo_detalhe'

class GrupoAtivo(models.Model):
    cod_grupo = models.AutoField(primary_key=True)
    desc_grupo = models.CharField(unique=True, max_length=250)

    def __str__(self):
        return self.desc_grupo

    class Meta:
        managed = False
        db_table = 'grupo_ativo'


class PrecoAtivo(models.Model):
    cod_preco = models.BigAutoField(primary_key=True)
    cod_ativo = models.ForeignKey(AtivoDetalhe, models.DO_NOTHING, db_column='cod_ativo')
    preco = models.FloatField()
    data = models.DateTimeField()

    def __str__(self):
        return str(self.cod_ativo) + '_' + str(self.data)

    class Meta:
        managed = False
        db_table = 'price'
        get_latest_by = '-data'

# ---- Managed models - Created in Django ----

class Portfolio (models.Model):
    nome = models.CharField(max_length=250)
    data_criacao = models.DateTimeField(auto_now=True)
    ativo = models.ManyToManyField(AtivoDetalhe, through='Aplicacao', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('portfolios:detail', kwargs={'pk':self.pk})

    def __str__(self):
        return '{}_{}'.format(self.nome, str(self.user))


class Aplicacao(models.Model):
    ativo = models.ForeignKey(AtivoDetalhe, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    data_aplicacao = models.DateField()
    preco_entrada = models.FloatField()
    taxa_entrada = models.FloatField(blank=True,null=True)
    valor_aplicado = models.FloatField()
    quantidade_aplicada = models.FloatField(blank=True, null=True)
    preco_atual = models.FloatField(blank=True, null=True)
    taxa_atual = models.FloatField(blank=True, null=True)
    rentabilidade_absoluta = models.FloatField(blank=True, null=True)
    rentabilidade_relativa = models.FloatField(blank=True, null=True)

    def __str__(self):
        return '{}_{}'.format(str(self.ativo), str(self.portfolio))
