from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from functools import reduce
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

class Preco_Custom_QuerySet(models.QuerySet):
    def get_last_prices_detail(self, listaAtivo):
        '''Retorna dados de aplicacao e valor atual de um portfolio de ativos a preço corrente'''
        anoAtual = datetime.date.today().year

        cleanTesouro= self.exclude(cod_ativo__sigla_ativo__contains='COMPRA-') # retirando da base titulos com dados referencia para COMPRA

        lastPrices = cleanTesouro.filter(cod_ativo__in=listaAtivo.keys()).order_by('cod_ativo', '-data').distinct('cod_ativo')
        prices = dict()
        for ativo, params in listaAtivo.items():
            for price in lastPrices:
                if ativo.desc_ativo == price.cod_ativo.desc_ativo:
                    preco = params['quantidade'] * price.preco
                    preco_unidade = price.preco
                    break

            if not preco:
                preco = 0
                preco_unidade = 0
            prices[ativo] = {'quantidade' : params['quantidade'],
                             'valor_aplicado' : params['valor_aplicado'],
                             'data_aplicacao' : params['data_aplicacao'],
                             'valor_total_atualizado' : preco,
                             'valor_atual_unitario' : preco_unidade }


        return prices

    def get_last_prices_unity(self, cod_ativo):
        '''retorna ultimo preço de um ativo em específico'''
        lastPrice = self.filter(cod_ativo=cod_ativo).order_by('-data').first()
        return lastPrice.preco



class Preco_Custom_Manager(models.Manager):
    def get_queryset(self):
        return Preco_Custom_QuerySet(self.model, using=self._db)  # Important!

    def get_last_prices_detail(self, listaAtivo):
        '''Retorna dados de aplicacao e valor atual de um portfolio de ativos a preço corrente'''
        return self.get_queryset().get_last_prices_detail(listaAtivo)

    def get_last_prices_unity(self, cod_ativo):
        '''retorna ultimo preço de um ativo em específico'''
        return self.get_queryset().get_last_prices_unity(cod_ativo)


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

class Proventos_Custom_QuerySet(models.QuerySet):
    def get_proventos_detail_unity(self, aplic):
        '''Retorna dados de aplicacao e os valores recebidos de proventos de um portfolio de ativos'''
        proventosAtivo = self.filter(cod_ativo=aplic.ativo).filter(data_com__gte=aplic.data_aplicacao).order_by('-data_com') # retirando da base titulos com dados referencia para COMPRA

        proventos = dict()
        for prov in proventosAtivo:
            proventos[prov.cod_provento] = {'valor': prov.valor_provento,
                                            'data_pagamento': prov.data_pagamento,
                                            'tipo' : prov.tipo_provento,
                                            'data_com': prov.data_com }
        return proventos

class Proventos_Custom_Manager(models.Manager):
    def get_queryset(self):
        return Proventos_Custom_QuerySet(self.model, using=self._db)  # Important!

    def get_proventos_detail_unity(self, ativo):
        '''Retorna dados de aplicacao e os valores recebidos de proventos de um portfolio de ativos'''
        return self.get_queryset().get_proventos_detail_unity(ativo)


class Proventos(models.Model):
    cod_provento = models.BigAutoField(primary_key=True)
    cod_ativo = models.ForeignKey(AtivoDetalhe, models.DO_NOTHING, db_column='cod_ativo')
    valor_provento = models.FloatField()
    data_com = models.DateField()
    data_pagamento = models.DateField()
    data_inclusao = models.DateTimeField()
    tipo_provento = models.CharField(max_length=250)
    customObjects = Proventos_Custom_Manager()

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

    class Meta:
        unique_together = ('nome', 'user')

class Aplicacao_Custom_Queryset(models.QuerySet):
    def get_tipoAplicacao_list(self, pk):
        '''Retorna uma lista com os tipos de ativos no portfolio'''
        aplicacoes = self.filter(portfolio=pk)
        types = {aplic.ativo.grupo_ativo.desc_grupo for aplic in aplicacoes}
        return types

    def get_ativos_list(self, pk):
        '''Retorna uma lista com os diferentes ativos no portfolio'''
        aplicacoes = self.filter(portfolio=pk)
        ativos = {aplic.ativo for aplic in aplicacoes}
        return ativos

    def get_aplic_list(self, pk):
        '''Retorna uma lista com os diferentes aplicações no portfolio'''
        aplicacoes = self.filter(portfolio=pk)
        aplics = {aplic for aplic in aplicacoes}
        return aplics

    def get_ativos_detail(self, pk):
        '''Retorna uma lista com os diferentes ativos e seus parametros unicos {ativo:{quantidade, valor aplicado}}'''
        aplicacoes = self.filter(portfolio=pk)
        ativos = dict([(aplic.ativo, {'quantidade':aplic.quantidade_aplicada,
                                      'valor_aplicado': aplic.valor_aplicado,
                                      'data_aplicacao': aplic.data_aplicacao }) for aplic in aplicacoes])
        return ativos

    def get_valor_aplicado_sum(self, pk):
        '''Retorna valor total aplicado no portfolio'''
        aplicacoes = self.filter(portfolio=pk)
        valores_entrada = [aplic.valor_aplicado for aplic in aplicacoes]
        soma_total = sum(valores_entrada)
        return soma_total

    def get_valor_byTipo(self, pk):
        '''Retorna dict com total aplicado por tipo de ativo no portfolio {tipo:{quantidade:total quantidade, 'valor:total valor}}'''
        aplicacoes = self.filter(portfolio=pk)
        types = {aplic.ativo.grupo_ativo.desc_grupo for aplic in aplicacoes}

        soma_tipo = dict()
        for tp in types:
            precos = [aplic.valor_aplicado for aplic in aplicacoes if aplic.ativo.grupo_ativo.desc_grupo == tp]
            qtds = [aplic.quantidade_aplicada for aplic in aplicacoes if aplic.ativo.grupo_ativo.desc_grupo == tp]
            soma_tipo[tp] = {'quantidade':sum(qtds), 'valor':sum(precos)}

        return soma_tipo

    def get_full_results(self, pk, aplicacoes,tiposAtivo ):
        '''input: aplicaçoes(get_aplic_list), tiposAtivo (get_tipoAplicacao_list) / retorna: aplicsDetalhe, valoresTipo, valoresTotais'''

        aplicsDetalhe = dict()
        contagem_ativos = []
        for aplic in aplicacoes:
            infoAtivo = dict()

            if aplic.ativo.grupo_ativo.cod_grupo in [4,5]:
                dias_IR =  datetime.date.today() - aplic.data_aplicacao
                dias_IR = dias_IR.days
                IR = 0
                if dias_IR <= 180:
                    IR = 0.225
                elif dias_IR > 180 and dias_IR <= 360:
                    IR = 0.20
                elif dias_IR > 360 and dias_IR <= 720:
                    IR = 0.175
                else:
                    IR = 0.15

                taxas_cdi = [((((x.preco*(1/252))*(aplic.taxa_entrada/100))/100)+1) for x in PrecoAtivo.objects.filter(cod_ativo=100000).filter(data__range=(aplic.data_aplicacao, datetime.date.today()))]

                multiplicador = reduce((lambda x, y: x * y), taxas_cdi)

                ganho_liq_IR = ((multiplicador-1) * aplic.quantidade_aplicada) * (1-IR)

                infoAtivo['ultimoPreco'] = 0
                infoAtivo['valorFinalAtualizado'] = aplic.quantidade_aplicada + ganho_liq_IR
                infoAtivo['ganhoNominalPreco'] = infoAtivo['valorFinalAtualizado'] - aplic.valor_aplicado
                infoAtivo['ganhoPercPreco'] = round((((infoAtivo['valorFinalAtualizado'] / aplic.valor_aplicado) - 1)*100), 1)

                infoAtivo['proventos'] = 0
                infoAtivo['ganhoNominalRendas'] = 0
                infoAtivo['ganhoPercRendas'] = 0
                infoAtivo['valorFinalAtualizadoRendas'] = infoAtivo['valorFinalAtualizado']

            else:

                ##pegando ultimo preço
                infoAtivo['ultimoPreco'] = PrecoAtivo.customObjects.get_last_prices_unity(aplic.ativo.pk)
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
                    proventosOficiais = Proventos.customObjects.get_proventos_detail_unity(aplic)
                    if proventosOficiais == {}:
                        infoAtivo['proventos'] = 0
                        infoAtivo['ganhoNominalRendas'] = infoAtivo['ganhoNominalPreco']
                        infoAtivo['ganhoPercRendas'] = infoAtivo['ganhoPercPreco']
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
        if valoresTotais['valorAplicado'] == 0 :
            valoresTotais['GanhoPerc'] = 0
        else:
            valoresTotais['GanhoPerc'] = round((((valoresTotais['valorAtualizado'] / valoresTotais['valorAplicado']) - 1)*100),1)
        valoresTotais['ganhoNominal'] = sum(valoresTotaisGanhoNominal)
        valoresTotais['proventos'] = sum(valoresTotaisProventos)
        valoresTotais['ganhoFinal'] = sum(valoresTotaisGanhoFinal)

        return aplicsDetalhe, valoresTipo, valoresTotais


class Aplicacao_Custom_Manager(models.Manager):
    def get_queryset(self):
        return Aplicacao_Custom_Queryset(self.model, using=self._db)  # Important!

    def get_tipoAplicacao_list(self, pk):
        '''Retorna uma lista com os tipos de ativos no portfolio'''
        return self.get_queryset().get_tipoAplicacao_list(pk)

    def get_ativos_list(self, pk):
        '''Retorna uma lista com os diferentes ativos no portfolio'''
        return self.get_queryset().get_ativos_list(pk)

    def get_aplic_list(self, pk):
        '''Retorna uma lista com os diferentes ativos no portfolio'''
        return self.get_queryset().get_aplic_list(pk)

    def get_ativos_detail(self, pk):
        '''Retorna uma lista com os diferentes ativos no portfolio'''
        return self.get_queryset().get_ativos_detail(pk)

    def get_valor_aplicado_sum(self, pk):
        '''Retorna valor total aplicado no portfolio'''
        return self.get_queryset().get_valor_aplicado_sum(pk)

    def get_valor_byTipo(self,pk):
        '''Retorna dict com total aplicado por tipo de ativo no portfolio {tipo:[total quantidade, total valor]}'''
        return self.get_queryset().get_valor_byTipo(pk)

    def get_full_results(self,pk, aplicacoes,tiposAtivo ):
        '''input: aplicaçoes(get_aplic_list), tiposAtivo (get_tipoAplicacao_list) / retorna: aplicsDetalhe, valoresTipo, valoresTotais'''
        return self.get_queryset().get_full_results(pk,aplicacoes,tiposAtivo)


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
        if self.ativo.grupo_ativo.cod_grupo == 3:
            return self.valor_aplicado / self.preco_entrada #arredondamento pra baixo, independente do restante no decimal
        else:
            return self.valor_aplicado // self.preco_entrada
