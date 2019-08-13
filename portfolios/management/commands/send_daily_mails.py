from django.core.management.base import BaseCommand
from django.templatetags.static import static
from HaluuraApp.settings import STATICFILES_DIRS
from django.core.mail import send_mail
from portfolios import models
from django.template import loader
import datetime

class Command(BaseCommand):
    help = 'send daily performance emails'

    def handle(self, *args, **kwargs):
        hoje = datetime.datetime.now().date().strftime("%d/%m/%Y")
        portfolios = models.Portfolio.objects.all()

        for portfolio in portfolios:
            ativos = models.Aplicacao.customObjects.get_ativos_list(portfolio.pk)
            aplicacoes = models.Aplicacao.customObjects.get_aplic_list(portfolio.pk)
            tiposAtivo = models.Aplicacao.customObjects.get_tipoAplicacao_list(portfolio.pk)

            aplicsDetalhe, valoresTipo, valoresTotais = models.Aplicacao.customObjects.get_full_results(portfolio.pk, aplicacoes, tiposAtivo)

            temAtivo = bool(ativos)
            user = portfolio.user
            userEmail = str(user.email)

            if temAtivo:

                html_message = loader.render_to_string(
                    'html_email_template.html',
                    {
                    'portfolio':portfolio,
                    'tipoAtivo': tiposAtivo,
                    'aplicacoes' : aplicsDetalhe,
                    'dadosTipo' : valoresTipo,
                    'dadosTotais': valoresTotais,
                    'hoje': hoje
                    }
                )
                enviar_email = send_mail(

                    subject='Desempenho Diário do seu Portfolio: {} - {}'.format(portfolio.nome, hoje),
                    from_email='Kapytalize <admin@kapytalize.com.br>',
                    recipient_list=[userEmail],
                    message='Teste',
                    html_message=html_message,
                    fail_silently=False,
                )

                enviar_email
                self.stdout.write('user: {}, ativos: {}, hoje:{}'.format(user.email, enviar_email, hoje))




            #self.stdout.write('Portfolio: {}, user: {}, ativos: {}'.format(portfolio.nome, user.email, temAtivo))
