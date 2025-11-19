# analytics/utils.py
# Utilitários para facilitar o rastreamento de eventos específicos

from .models import AccessLog


def track_calculation(request, calculation_type, details=None):
    """
    Função auxiliar para rastrear cálculos específicos
    
    Args:
        request: HttpRequest object
        calculation_type: Tipo do cálculo ('potencia', 'espiras', 'diagrama')
        details: Dicionário com detalhes adicionais do cálculo
    
    Exemplo de uso:
        track_calculation(request, 'potencia', {
            'diametro': 100,
            'comprimento': 200,
            'polos': 4,
            'resultado_kw': 5.5
        })
    """
    if hasattr(request, 'access_log'):
        # Atualiza o log existente
        request.access_log.access_type = 'calculation'
        request.access_log.calculation_type = calculation_type
        request.access_log.save(update_fields=['access_type', 'calculation_type'])
        
        # Se quiser salvar detalhes adicionais, pode criar um modelo separado
        # ou usar um campo JSON no AccessLog
    
    return True


def get_user_location(request):
    """
    Retorna a localização do usuário atual
    
    Returns:
        dict: Dicionário com cidade, estado e país
    """
    if hasattr(request, 'access_log'):
        return {
            'city': request.access_log.city,
            'state': request.access_log.state,
            'country': request.access_log.country,
            'latitude': request.access_log.latitude,
            'longitude': request.access_log.longitude,
        }
    return None


def get_user_stats(ip_address):
    """
    Retorna estatísticas de um usuário específico
    
    Args:
        ip_address: IP do usuário
    
    Returns:
        dict: Estatísticas do usuário
    """
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    logs = AccessLog.objects.filter(ip_address=ip_address)
    
    return {
        'total_visits': logs.count(),
        'total_calculations': logs.filter(access_type='calculation').count(),
        'first_visit': logs.order_by('timestamp').first().timestamp if logs.exists() else None,
        'last_visit': logs.order_by('-timestamp').first().timestamp if logs.exists() else None,
        'calculations_by_type': logs.filter(access_type='calculation').values(
            'calculation_type'
        ).annotate(count=Count('id')),
    }


# =====================================================
# EXEMPLO DE INTEGRAÇÃO NAS VIEWS EXISTENTES
# =====================================================

"""
# Exemplo de como integrar nas suas views existentes:

# ThreePhasePower/views.py

from django.shortcuts import render, redirect
from analytics.utils import track_calculation

def calculo_view(request):
    if request.method == 'POST':
        form = CalculoForm(request.POST)
        
        if form.is_valid():
            # Processa o cálculo
            resultado = calcular_potencia(
                diametro=form.cleaned_data['diametro'],
                comprimento=form.cleaned_data['comprimento'],
                polos=form.cleaned_data['polos'],
                frequencia=form.cleaned_data['frequencia']
            )
            
            # ADICIONE ESTA LINHA para rastrear o cálculo
            track_calculation(request, 'potencia', {
                'diametro': form.cleaned_data['diametro'],
                'comprimento': form.cleaned_data['comprimento'],
                'polos': form.cleaned_data['polos'],
                'resultado_kw': resultado['potencia_kw']
            })
            
            return render(request, 'calculo.html', {
                'form': form,
                'resultado': resultado
            })
    else:
        form = CalculoForm()
    
    return render(request, 'calculo.html', {'form': form})


# ThreePhaseCoils/views.py

from analytics.utils import track_calculation

def espiras_view(request):
    if request.method == 'POST':
        form = EspirasForm(request.POST)
        
        if form.is_valid():
            # Processa o cálculo
            resultado = calcular_espiras(
                ranhuras=form.cleaned_data['ranhuras'],
                polos=form.cleaned_data['polos'],
                tensao=form.cleaned_data['tensao'],
                potencia=form.cleaned_data['potencia']
            )
            
            # ADICIONE ESTA LINHA para rastrear o cálculo
            track_calculation(request, 'espiras', {
                'ranhuras': form.cleaned_data['ranhuras'],
                'polos': form.cleaned_data['polos'],
                'tensao': form.cleaned_data['tensao'],
                'potencia': form.cleaned_data['potencia'],
                'espiras_calculadas': resultado['espiras']
            })
            
            return render(request, 'espiras.html', {
                'form': form,
                'resultado': resultado
            })
    else:
        form = EspirasForm()
    
    return render(request, 'espiras.html', {'form': form})


# ThreePhaseDiagram/views.py

from analytics.utils import track_calculation, get_user_location

def diagrama_view(request):
    # Exemplo de uso da localização do usuário
    user_location = get_user_location(request)
    
    if request.method == 'POST':
        # Processa geração do diagrama
        diagrama = gerar_diagrama(request.POST)
        
        # ADICIONE ESTA LINHA para rastrear
        track_calculation(request, 'diagrama', {
            'tipo_diagrama': request.POST.get('tipo'),
            'localizacao': user_location
        })
        
        return render(request, 'diagrama.html', {
            'diagrama': diagrama,
            'location': user_location  # Pode mostrar de onde o usuário está acessando
        })
    
    return render(request, 'diagrama.html', {
        'location': user_location
    })
"""

# =====================================================
# EXEMPLO DE VIEW PERSONALIZADA DE ESTATÍSTICAS
# =====================================================

"""
# Você pode criar uma view pública de estatísticas

# analytics/views.py

from django.shortcuts import render
from django.db.models import Count
from datetime import datetime, timedelta
from .models import AccessLog

def estatisticas_publicas(request):
    # Estatísticas dos últimos 30 dias
    start_date = datetime.now() - timedelta(days=30)
    
    logs = AccessLog.objects.filter(
        timestamp__gte=start_date,
        is_bot=False
    )
    
    context = {
        'total_calculos': logs.filter(access_type='calculation').count(),
        'estados_atendidos': logs.values('state').distinct().count(),
        'cidades_atendidas': logs.values('city').distinct().count(),
        'calculos_por_tipo': logs.filter(
            access_type='calculation'
        ).values('calculation_type').annotate(
            total=Count('id')
        ),
        'top_estados': logs.exclude(state='').values('state').annotate(
            total=Count('id')
        ).order_by('-total')[:5]
    }
    
    return render(request, 'analytics/estatisticas_publicas.html', context)
"""

# =====================================================
# EXEMPLO DE COMANDO PARA GERAR RELATÓRIOS
# =====================================================

"""
# Crie um comando Django para gerar relatórios por email

# analytics/management/commands/relatorio_semanal.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.db.models import Count
from datetime import datetime, timedelta
from analytics.models import AccessLog

class Command(BaseCommand):
    help = 'Envia relatório semanal de analytics por email'
    
    def handle(self, *args, **options):
        # Dados da última semana
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        logs = AccessLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date,
            is_bot=False
        )
        
        # Gera estatísticas
        total_visits = logs.count()
        unique_visitors = logs.values('ip_address').distinct().count()
        total_calculations = logs.filter(access_type='calculation').count()
        
        top_states = logs.exclude(state='').values('state').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Monta o email
        subject = f'Relatório Semanal - MotorCalcPro - {start_date.strftime("%d/%m")} a {end_date.strftime("%d/%m")}'
        
        message = f\"\"\"
        RELATÓRIO SEMANAL DE ANALYTICS
        ================================
        
        Período: {start_date.strftime("%d/%m/%Y")} a {end_date.strftime("%d/%m/%Y")}
        
        RESUMO GERAL:
        - Total de Visitas: {total_visits}
        - Visitantes Únicos: {unique_visitors}
        - Cálculos Realizados: {total_calculations}
        
        TOP 5 ESTADOS:
        \"\"\"
        
        for i, state in enumerate(top_states, 1):
            message += f"{i}. {state['state']}: {state['count']} acessos\\n"
        
        # Envia o email
        send_mail(
            subject,
            message,
            'sistema@motorcalcpro.com.br',
            ['admin@motorcalcpro.com.br'],
            fail_silently=False,
        )
        
        self.stdout.write(self.style.SUCCESS('Relatório enviado com sucesso!'))

# Execute com: python manage.py relatorio_semanal
# Ou agende no cron para executar toda segunda-feira:
# 0 9 * * 1 /usr/bin/python /path/to/manage.py relatorio_semanal
"""