from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
import datetime

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

class Preco_Custom_Manager(models.Manager):
    def get_price_range_currentYear(self, listaAtivo, year):
        '''Retorna query com ativos selecionados, no ano de escolha'''
        firstDayYear = datetime.date(year, 1, 1)
        lastDayYear = datetime.date(year,12,31)

        price_range = self.filter(cod_ativo_desc_ativo__in=listaAtivo).filter(data__range=(firstDayYear, lastDayYear))

        return price_range


class PrecoAtivo(models.Model):
    cod_preco = models.BigAutoField(primary_key=True)
    cod_ativo = models.ForeignKey(AtivoDetalhe, models.DO_NOTHING, db_column='cod_ativo')
    preco = models.FloatField()
    data = models.DateTimeField()
    objects = models.Manager()
    customObjects = Preco_Custom_Manager()

    def __str__(self):
        return str(self.cod_ativo) + '_' + str(self.data)

    class Meta:
        managed = False
        db_table = 'price'
        get_latest_by = '-data'


class Proventos(models.Model):
    cod_provento = models.BigAutoField(primary_key=True)
    cod_ativo = models.ForeignKey(AtivoDetalhe, models.DO_NOTHING, db_column='cod_ativo')
    valor_provento = models.FloatField()
    data_com = models.DateField()
    data_pagamento = models.DateField()
    data_inclusao = models.DateTimeField()
    tipo_provento = models.CharField(max_length=250)

    class Meta:
        managed = False
        db_table = 'proventos'
        unique_together = (('cod_ativo', 'valor_provento', 'data_com', 'tipo_provento'),)


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

class Aplicacao_Custom_Queryset(models.QuerySet):
    def get_tipoAplicacao_list(self, pk):
        '''Retorna uma lista com os tipos de ativos no portfolio'''
        aplicacoes = self.filter(portfolio=pk)
        types = {aplic.ativo.grupo_ativo.desc_grupo for aplic in aplicacoes}
        return types

    def get_ativos_list(self, pk):
        '''Retorna uma lista com os diferentes ativos no portfolio'''
        aplicacoes = self.filter(portfolio=pk)
        ativos = {aplic.ativo.desc_ativo for aplic in aplicacoes}
        return ativos

    def get_valor_aplicado_sum(self, pk):
        '''Retorna valor total aplicado no portfolio'''
        aplicacoes = self.filter(portfolio=pk)
        valores_entrada = [aplic.valor_aplicado for aplic in aplicacoes]
        soma_total = sum(valores_entrada)
        return soma_total

    def get_valor_byTipo(self, pk):
        '''Retorna dict com total aplicado por tipo de ativo no portfolio {tipo:[total quantidade, total valor]}'''
        aplicacoes = self.filter(portfolio=pk)
        types = {aplic.ativo.grupo_ativo.desc_grupo for aplic in aplicacoes}

        soma_tipo = dict()
        for tp in types:
            precos = [aplic.valor_aplicado for aplic in aplicacoes if aplic.ativo.grupo_ativo.desc_grupo == tp]
            qtds = [aplic.quantidade_aplicada for aplic in aplicacoes if aplic.ativo.grupo_ativo.desc_grupo == tp]
            soma_tipo[tp] = [sum(qtds),sum(precos)]

        return soma_tipo


class Aplicacao_Custom_Manager(models.Manager):
    def get_queryset(self):
        return Aplicacao_Custom_Queryset(self.model, using=self._db)  # Important!

    def get_tipoAplicacao_list(self, pk):
        '''Retorna uma lista com os tipos de ativos no portfolio'''
        return self.get_queryset().get_tipoAplicacao_list(pk)

    def get_ativos_list(self, pk):
        '''Retorna uma lista com os diferentes ativos no portfolio'''
        return self.get_queryset().get_ativos_list(pk)

    def get_valor_aplicado_sum(self, pk):
        '''Retorna valor total aplicado no portfolio'''
        return self.get_queryset().get_valor_aplicado_sum(pk)

    def get_valor_byTipo(self,pk):
        '''Retorna dict com total aplicado por tipo de ativo no portfolio {tipo:[total quantidade, total valor]}'''
        return self.get_queryset().get_valor_byTipo(pk)


class Aplicacao(models.Model):
    ativo = models.ForeignKey(AtivoDetalhe, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    data_aplicacao = models.DateField()
    preco_entrada = models.FloatField()
    taxa_entrada = models.FloatField(blank=True,null=True)
    valor_aplicado = models.FloatField()
    preco_atual = models.FloatField(blank=True, null=True)
    taxa_atual = models.FloatField(blank=True, null=True)
    rentabilidade_absoluta = models.FloatField(blank=True, null=True)
    rentabilidade_relativa = models.FloatField(blank=True, null=True)
    objects = models.Manager()
    customObjects = Aplicacao_Custom_Manager()

    def __str__(self):
        return '{}_{}'.format(str(self.ativo), str(self.portfolio))

    @property
    def quantidade_aplicada(self):
        return self.valor_aplicado // self.preco_entrada #arredondamento pra baixo, independente do restante no decimal
