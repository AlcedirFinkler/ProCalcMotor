from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import MotorCalculoForm, CarcacaSelecaoForm
import math
import json

##########################################################################
############### Etapa de calculo da potência do motor ##################
##########################################################################

def calcular_potencia_motor(diametro_mm, comprimento_mm, polos, frequencia):
    """
    Calcula a potência estimada do motor baseado em suas dimensões.
    """
    # Converter dimensões de mm para metros
    D_m = diametro_mm / 1000
    L_m = comprimento_mm / 1000
    
    # Calcular velocidade síncrona em rpm
    n_s = (120 * frequencia) / polos
    
    # CÁLCULO REVISADO: Fórmula mais precisa para motores pequenos
    volume_mm3 = (diametro_mm ** 2) * comprimento_mm
    
    # Fator K revisado baseado em dados reais de motores
    if volume_mm3 < 220000:  # <1CV
        K = 1100 
    elif volume_mm3 < 860000:  # <5CV
        K = 1400 
    elif volume_mm3 < 1720000:  # <10CV
        K = 1500 
    elif volume_mm3 < 2350000:  # <15CV
        K = 1500
    elif volume_mm3 < 4150000:  # <25CV
        K = 1500
    elif volume_mm3 < 6600000:  # <40CV
        K = 1540
    else:  # Motores maiores (>40CV)
        K = 1550
    
    # Fator de correção para número de polos
    fator_polos = {
        2: 0.85,
        4: 1.00,
        6: 1.12,
        8: 1.18,
        10: 1.22,
        12: 1.25
    }.get(polos, 1.0)
    
    # Calcular potência: P = K × D² × L × n_s × fator_polos
    P_watts = K * (D_m ** 2) * L_m * n_s * fator_polos
    
    # Potência em kW
    P_kw = P_watts / 1000
    
    # Potência em CV (1 CV = 0,7355 kW)
    P_cv = P_kw / 0.7355
    
    # Dados básicos
    resultado = {
        'potencia_kw': round(P_kw, 3),
        'potencia_cv': round(P_cv, 3),
        'velocidade_sincrona': round(n_s, 1),
        'coeficiente_k': round(K, 2),
        'fator_polos': round(fator_polos, 2),
        'diametro_m': round(D_m, 4),
        'comprimento_m': round(L_m, 4),
    }
    
    # TABELA 21 ATUALIZADA: Incluídos dados para 10 e 12 polos
    tabela_21 = {
        '63': {2: (0.12, 0.75), 4: (0.12, 0.75)},
        '71': {2: (0.75, 1.1), 4: (0.75, 1.1)},
        '80': {2: (1.1, 1.5), 4: (0.75, 1.1)},
        '90S': {2: (1.5, 2.2), 4: (1.1, 1.5), 6: (0.75, 1.1), 8: (0.55, 0.75)},
        '90L': {2: (2.2, 3.0), 4: (1.5, 2.2), 6: (1.1, 1.5), 8: (0.75, 1.1)},
        '100L': {2: (3.0, 4.0), 4: (2.2, 3.0), 6: (1.5, 2.2), 8: (1.1, 1.5),
                 10: (0.75, 1.1), 12: (0.55, 0.75)},
        '112M': {2: (4.0, 5.5), 4: (3.0, 4.0), 6: (2.2, 3.0), 8: (1.5, 2.2),
                 10: (1.1, 1.5), 12: (0.75, 1.1)},
        '132S': {2: (5.5, 7.5), 4: (4.0, 5.5), 6: (3.0, 4.0), 8: (2.2, 3.0),
                 10: (1.5, 2.2), 12: (1.1, 1.5)},
        '132M': {2: (7.5, 11.0), 4: (5.5, 7.5), 6: (4.0, 5.5), 8: (3.0, 4.0),
                 10: (2.2, 3.0), 12: (1.5, 2.2)},
        '160M': {2: (11.0, 15.0), 4: (7.5, 11.0), 6: (5.5, 7.5), 8: (4.0, 5.5),
                 10: (3.0, 4.0), 12: (2.2, 3.0)},
        '160L': {2: (15.0, 18.5), 4: (11.0, 15.0), 6: (7.5, 11.0), 8: (5.5, 7.5),
                 10: (4.0, 5.5), 12: (3.0, 4.0)},
        '180M': {2: (18.5, 22.0), 4: (15.0, 18.5), 6: (11.0, 15.0), 8: (7.5, 11.0),
                 10: (5.5, 7.5), 12: (4.0, 5.5)},
        '180L': {2: (22.0, 30.0), 4: (18.5, 22.0), 6: (15.0, 18.5), 8: (11.0, 15.0),
                 10: (7.5, 11.0), 12: (5.5, 7.5)},
        '200L': {2: (30.0, 37.0), 4: (22.0, 30.0), 6: (18.5, 22.0), 8: (15.0, 18.5),
                 10: (11.0, 15.0), 12: (7.5, 11.0)},
        '225S/M': {2: (37.0, 55.0), 4: (30.0, 45.0), 6: (22.0, 37.0), 8: (18.5, 30.0),
                   10: (15.0, 22.0), 12: (11.0, 15.0)},
        '250S/M': {2: (55.0, 75.0), 4: (45.0, 60.0), 6: (30.0, 45.0), 8: (22.0, 37.0),
                   10: (18.5, 30.0), 12: (15.0, 18.5)},
        '280S/M': {2: (75.0, 110.0), 4: (60.0, 90.0), 6: (45.0, 75.0), 8: (30.0, 55.0),
                   10: (22.0, 37.0), 12: (18.5, 22.0)},
        '315S/M': {2: (110.0, 160.0), 4: (90.0, 132.0), 6: (75.0, 110.0), 8: (55.0, 90.0),
                   10: (30.0, 55.0), 12: (22.0, 30.0)},
        '355M/L': {2: (160.0, 250.0), 4: (132.0, 200.0), 6: (110.0, 160.0), 8: (75.0, 132.0),
                   10: (37.0, 75.0), 12: (30.0, 45.0)},
        '355A/B': {2: (250.0, 315.0), 4: (200.0, 250.0), 6: (160.0, 200.0), 8: (110.0, 160.0),
                   10: (55.0, 110.0), 12: (37.0, 55.0)},
        '400': {2: (250.0, 500.0), 4: (200.0, 400.0), 6: (160.0, 315.0), 8: (110.0, 250.0),
                10: (75.0, 160.0), 12: (55.0, 90.0)}
    }
    
    def avaliar_carcaças(p_kw, polos, tabela):
        sugestoes = []
        inconsistencia = None
        diff_min = float('inf')
        carcaça_proxima = None
        faixa_proxima = None
        
        for carcaça, dados_polos in tabela.items():
            if polos in dados_polos:
                min_p, max_p = dados_polos[polos]
                if min_p <= p_kw <= max_p:
                    potencia_sugerida = round(max(min_p, min(max_p, p_kw)), 1)
                    sugestoes.append({
                        'carcaça': carcaça,
                        'faixa_kw': f'{min_p}-{max_p}',
                        'sugestão': f'Modelo {carcaça}: potência nominal sugerida {potencia_sugerida} kW baseada na norma IEC 60072-1'
                    })
                else:
                    diff = abs(p_kw - (min_p + max_p) / 2)
                    if diff < diff_min:
                        diff_min = diff
                        carcaça_proxima = carcaça
                        faixa_proxima = f'{min_p}-{max_p}'
        
        if not sugestoes:
            if carcaça_proxima:
                diff_percent = (diff_min / p_kw) * 100 if p_kw > 0 else 0
                if diff_percent > 20:
                    inconsistencia = f'Inconsistência: Potência estimada ({p_kw:.1f} kW) fora da faixa padrão para {polos} polos (próxima: {carcaça_proxima}, {faixa_proxima} kW; diferença ~{diff_percent:.0f}%)'
                else:
                    sugestoes.append({
                        'carcaça': carcaça_proxima,
                        'faixa_kw': faixa_proxima,
                        'sugestão': f'Próximo modelo WEG W22 {carcaça_proxima}: verifique faixa {faixa_proxima} kW'
                    })
            else:
                inconsistencia = f'Inconsistência: Nenhuma carcaça padrão encontrada para {polos} polos e {p_kw:.1f} kW'
        
        return {
            'sugestoes': sugestoes,
            'inconsistencia': inconsistencia
        }
    
    avaliacao = avaliar_carcaças(P_kw, polos, tabela_21)
    resultado['avaliacao_carcaça'] = avaliacao
    
    return resultado

def obter_potencias_por_carcaca(carcaca):
    """
    Retorna as potências disponíveis para uma carcaça específica.
    """
    tabela_carcacas = {
        '63': {2: (0.12, 0.75), 4: (0.12, 0.75)},
        '71': {2: (0.75, 1.1), 4: (0.75, 1.1)},
        '80': {2: (1.1, 1.5), 4: (0.75, 1.1)},
        '90S': {2: (1.5, 2.2), 4: (1.1, 1.5), 6: (0.75, 1.1), 8: (0.55, 0.75)},
        '90L': {2: (2.2, 3.0), 4: (1.5, 2.2), 6: (1.1, 1.5), 8: (0.75, 1.1)},
        '100L': {2: (3.0, 4.0), 4: (2.2, 3.0), 6: (1.5, 2.2), 8: (1.1, 1.5),
                 10: (0.75, 1.1), 12: (0.55, 0.75)},
        '112M': {2: (4.0, 5.5), 4: (3.0, 4.0), 6: (2.2, 3.0), 8: (1.5, 2.2),
                 10: (1.1, 1.5), 12: (0.75, 1.1)},
        '132S': {2: (5.5, 7.5), 4: (4.0, 5.5), 6: (3.0, 4.0), 8: (2.2, 3.0),
                 10: (1.5, 2.2), 12: (1.1, 1.5)},
        '132M': {2: (7.5, 11.0), 4: (5.5, 7.5), 6: (4.0, 5.5), 8: (3.0, 4.0),
                 10: (2.2, 3.0), 12: (1.5, 2.2)},
        '160M': {2: (11.0, 15.0), 4: (7.5, 11.0), 6: (5.5, 7.5), 8: (4.0, 5.5),
                 10: (3.0, 4.0), 12: (2.2, 3.0)},
        '160L': {2: (15.0, 18.5), 4: (11.0, 15.0), 6: (7.5, 11.0), 8: (5.5, 7.5),
                 10: (4.0, 5.5), 12: (3.0, 4.0)},
        '180M': {2: (18.5, 22.0), 4: (15.0, 18.5), 6: (11.0, 15.0), 8: (7.5, 11.0),
                 10: (5.5, 7.5), 12: (4.0, 5.5)},
        '180L': {2: (22.0, 30.0), 4: (18.5, 22.0), 6: (15.0, 18.5), 8: (11.0, 15.0),
                 10: (7.5, 11.0), 12: (5.5, 7.5)},
        '200L': {2: (30.0, 37.0), 4: (22.0, 30.0), 6: (18.5, 22.0), 8: (15.0, 18.5),
                 10: (11.0, 15.0), 12: (7.5, 11.0)},
        '225S/M': {2: (37.0, 55.0), 4: (30.0, 45.0), 6: (22.0, 37.0), 8: (18.5, 30.0),
                   10: (15.0, 22.0), 12: (11.0, 15.0)},
        '250S/M': {2: (55.0, 75.0), 4: (45.0, 60.0), 6: (30.0, 45.0), 8: (22.0, 37.0),
                   10: (18.5, 30.0), 12: (15.0, 18.5)},
        '280S/M': {2: (75.0, 110.0), 4: (60.0, 90.0), 6: (45.0, 75.0), 8: (30.0, 55.0),
                   10: (22.0, 37.0), 12: (18.5, 22.0)},
        '315S/M': {2: (110.0, 160.0), 4: (90.0, 132.0), 6: (75.0, 110.0), 8: (55.0, 90.0),
                   10: (30.0, 55.0), 12: (22.0, 30.0)},
        '355M/L': {2: (160.0, 250.0), 4: (132.0, 200.0), 6: (110.0, 160.0), 8: (75.0, 132.0),
                   10: (37.0, 75.0), 12: (30.0, 45.0)},
        '355A/B': {2: (250.0, 315.0), 4: (200.0, 250.0), 6: (160.0, 200.0), 8: (110.0, 160.0),
                   10: (55.0, 110.0), 12: (37.0, 55.0)},
        '400': {2: (250.0, 500.0), 4: (200.0, 400.0), 6: (160.0, 315.0), 8: (110.0, 250.0),
                10: (75.0, 160.0), 12: (55.0, 90.0)}
    }
    
    if carcaca not in tabela_carcacas:
        return None
    
    potencias_por_polo = []
    dados_carcaca = tabela_carcacas[carcaca]
    
    for num_polos in sorted(dados_carcaca.keys()):
        min_kw, max_kw = dados_carcaca[num_polos]
        velocidade_60hz = (120 * 60) / num_polos
        min_cv = min_kw * 1.341
        max_cv = max_kw * 1.341
        
        potencias_por_polo.append({
            'polos': num_polos,
            'potencia_min_kw': round(min_kw, 2),
            'potencia_max_kw': round(max_kw, 2),
            'potencia_min_cv': round(min_cv, 2),
            'potencia_max_cv': round(max_cv, 2),
            'velocidade_sincrona_rpm': round(velocidade_60hz, 0),
            'faixa_kw': f"{min_kw} - {max_kw} kW",
            'faixa_cv': f"{round(min_cv, 1)} - {round(max_cv, 1)} CV"
        })
    
    return {
        'carcaca': carcaca,
        'potencias': potencias_por_polo
    }

def calculo(request):
    """
    View que gerencia dois tipos de cálculo:
    1. Por dimensões (diâmetro e comprimento)
    2. Por seleção de carcaça
    """
    resultado = None
    resultado_carcaca = None
    metodo = request.POST.get('metodo', 'dimensoes')
    
    if request.method == 'POST':
        if metodo == 'dimensoes':
            form_dimensoes = MotorCalculoForm(request.POST)
            form_carcaca = CarcacaSelecaoForm()
            
            if form_dimensoes.is_valid():
                diametro = form_dimensoes.cleaned_data['diametro']
                comprimento = form_dimensoes.cleaned_data['comprimento']
                polos = int(form_dimensoes.cleaned_data['polos'])
                frequencia = int(form_dimensoes.cleaned_data['frequencia'])
                
                resultado = calcular_potencia_motor(diametro, comprimento, polos, frequencia)
                resultado['dados_entrada'] = {
                    'diametro': diametro,
                    'comprimento': comprimento,
                    'polos': polos,
                    'frequencia': frequencia
                }
        elif metodo == 'carcaca':
            form_carcaca = CarcacaSelecaoForm(request.POST)
            form_dimensoes = MotorCalculoForm()
            
            if form_carcaca.is_valid():
                carcaca = form_carcaca.cleaned_data['carcaca']
                resultado_carcaca = obter_potencias_por_carcaca(carcaca)
    
    form_dimensoes = locals().get('form_dimensoes', MotorCalculoForm())
    form_carcaca = locals().get('form_carcaca', CarcacaSelecaoForm())
    
    return render(request, 'calculo.html', {
        'form_dimensoes': form_dimensoes,
        'form_carcaca': form_carcaca,
        'resultado': resultado,
        'resultado_carcaca': resultado_carcaca,
        'metodo': metodo
    })
