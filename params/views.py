from django.shortcuts import render
from django.db.models import Q
from datetime import (date,datetime,timedelta)
from django.http import HttpResponse,JsonResponse

# Create your views here.
from .models import (ColecaoB2b,ColecaoErp,Banner,Parametro)
from core.models import (Periodo,Cliente)

def params(request):
    
    cols_erp = list(ColecaoErp.objects.filter(colecaoB2b__active=True).values_list('codigo', flat=True).distinct())
    tabelas = list(Cliente.objects.all().values_list('tabela_precos', flat=True).distinct())
    periodos = list(Periodo.objects.filter(Q(periodo_faturamento__gt=date.today()) | Q(desc_periodo__in=['Imediato','Pre-selecionados'])).order_by(
                'periodo_faturamento').values())
    ultima_atualizacao_clientes = Parametro.objects.get(parametro='ULTIMA_ATUALIZACAO_CLIENTES').valor
    ultima_atualizacao_produtos = Parametro.objects.get(parametro='ULTIMA_ATUALIZACAO_PRODUTOS').valor
    colecao_vigente = Parametro.objects.get(parametro='COLECAO_VIGENTE').valor
    return JsonResponse({'cols': cols_erp,'tabelas':tabelas,'periodos':periodos,
    'ultima_atualizacao_clientes':ultima_atualizacao_clientes,
    'ultima_atualizacao_produtos':ultima_atualizacao_produtos,'colecao_vigente':colecao_vigente})

def filterOptions(request):
    
    colecoes = list(ColecaoB2b.objects.filter(active=True).order_by('ordem').values_list('title', flat=True).distinct())
    periodos = list(Periodo.objects.filter(Q(periodo_faturamento__gt=date.today()) | Q(desc_periodo__in=['Imediato','30 dias'])).order_by(
                'periodo_faturamento').values_list('desc_periodo', flat=True).distinct())
    return JsonResponse({'colecoes': colecoes,'periodos':periodos})