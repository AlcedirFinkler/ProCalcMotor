from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ThreePhaseCoils.models import MotorConfiguration
from .forms import ConfiguracaoMotorForm

# ========================================
# 📊 TABELA AWG PARA FIOS ESMALTADOS
# ========================================
# Dicionário: {area_mm2: (awg, descricao)}
# Valores exatos em mm² (seção transversal). Ordenado por área decrescente.
# Fonte: Padrão AWG para fios sólidos esmaltados (faixa comercial para bobinagem).
AWG_TABLE = {
    107.2190: (-4, '4/0 AWG'),
    85.0120: (-3, '3/0 AWG'),
    67.4350: (-2, '2/0 AWG'),
    53.4750: (-1, '1/0 AWG'),
    42.4140: (1, '1 AWG'),
    33.6270: (2, '2 AWG'),
    26.6730: (3, '3 AWG'),
    21.1500: (4, '4 AWG'),
    16.7720: (5, '5 AWG'),
    13.3010: (6, '6 AWG'),
    10.5480: (7, '7 AWG'),
    8.36670: (8, '8 AWG'),
    6.63320: (9, '9 AWG'),
    5.26100: (10, '10 AWG'),
    4.17280: (11, '11 AWG'),
    3.30990: (12, '12 AWG'),
    2.62470: (13, '13 AWG'),
    2.08090: (14, '14 AWG'),
    1.65070: (15, '15 AWG'),
    1.30900: (16, '16 AWG'),
    1.03790: (17, '17 AWG'),
    0.82300: (18, '18 AWG'),
    0.65270: (19, '19 AWG'),
    0.51760: (20, '20 AWG'),
    0.41050: (21, '21 AWG'),
    0.32550: (22, '22 AWG'),
    0.25800: (23, '23 AWG'),
    0.20470: (24, '24 AWG'),
    0.16240: (25, '25 AWG'),
    0.12890: (26, '26 AWG'),
    0.10230: (27, '27 AWG'),
    0.08110: (28, '28 AWG'),
    0.06430: (29, '29 AWG'),
    0.05090: (30, '30 AWG'),
    0.04040: (31, '31 AWG'),
    0.03200: (32, '32 AWG'),
    0.02540: (33, '33 AWG'),
    0.02010: (34, '34 AWG'),
    0.01590: (35, '35 AWG'),
    0.01270: (36, '36 AWG'),
    0.01000: (37, '37 AWG'),
    0.00800: (38, '38 AWG'),
    0.00630: (39, '39 AWG'),
    0.00500: (40, '40 AWG'),
}

# CORREÇÃO: Lista global ordenada por área ASCENDENTE (para next_larger eficiente)
# Formato: [(area, awg, desc), ...] — menor área primeiro
GAUGES_SORTED_ASC = sorted([(area, awg, desc) for area, (awg, desc) in AWG_TABLE.items()], key=lambda x: x[0])

def get_awg_for_area(area_mm2, mode='next_larger'):
    """
    Busca o AWG dado a área em mm².
    
    Args:
        area_mm2 (float): Área calculada (ex.: 1.25).
        mode (str): 'closest' (mais próximo) ou 'next_larger' (próximo maior ou igual, recomendado para segurança em motores).
    
    Returns:
        dict: {'awg': int, 'descricao': str, 'area_mm2': float, 'diferenca': float} ou None.
    
    Exemplo:
        get_awg_for_area(0.057)  # {'awg': 29, 'descricao': '29 AWG', 'area_mm2': 0.0643, 'diferenca': 0.0073}
    """
    if area_mm2 <= 0:
        return None
    
    global GAUGES_SORTED_ASC  # Usa a lista pré-ordenada
    
    if mode == 'closest':
        # CORREÇÃO: Não depende de ordem; usa min por diferença (lógica OK)
        closest = min(GAUGES_SORTED_ASC, key=lambda g: abs(g[0] - area_mm2))
        diff = abs(closest[0] - area_mm2)
        return {
            'awg': closest[1],
            'descricao': closest[2],
            'area_mm2': closest[0],
            'diferenca': round(diff, 4)  # Adicionado para debug
        }
    
    elif mode == 'next_larger':
        # CORREÇÃO: Ordenação ASCENDENTE garante que o primeiro >= seja o menor área suficiente
        for area, awg, desc in GAUGES_SORTED_ASC:
            if area >= area_mm2:
                diff = area - area_mm2
                return {
                    'awg': awg,
                    'descricao': desc,
                    'area_mm2': area,
                    'diferenca': round(diff, 4)  # Adicionado para debug
                }
        # Se area_mm2 > maior área, retorna o maior fio disponível
        maior_fio = GAUGES_SORTED_ASC[-1]
        return {
            'awg': maior_fio[1],
            'descricao': maior_fio[2],
            'area_mm2': maior_fio[0],
            'diferenca': round(maior_fio[0] - area_mm2, 4)  # Negativo se insuficiente
        }
    
    return None

def calculo_espiras(request):
    if request.method == 'POST':
        form = ConfiguracaoMotorForm(request.POST)

        # Valores enviados no POST
        S_post = request.POST.get('S')
        P_post = request.POST.get('P')
        Camada_post = request.POST.get('Camada')
        g_type_post = request.POST.get('g_type')
        y_post = request.POST.get('y')

        # ========================================
        # 🔥 RECONSTRUIR TODOS OS CHOICES DINÂMICOS
        # ========================================

        # -------- S (ranhuras) --------
        ranhuras = MotorConfiguration.objects.values_list('S', flat=True).distinct().order_by('S')
        form.fields['S'].choices = [
            ('', '--- Selecione o número de ranhuras ---')
        ] + [(str(s), f"{s} ranhuras") for s in ranhuras]

        # -------- P (polos) --------
       # -------- P (polos) --------
        if S_post:
            try:
                S_int = int(S_post)
                polos = MotorConfiguration.get_polos_disponiveis(S_int)
                form.fields['P'].choices = [
                    ('', '--- Selecione o número de polos ---')
                ] + [(str(p), f"{p} polos") for p in polos]
            except:
                form.fields['P'].choices = [('', '--- Selecione o número de polos ---')]
                S_int = None  # ← Definir S_int como None se houver erro

        # -------- Camada --------
        if S_post and P_post and S_int is not None:  # ← Verificar se S_int existe
            try:
                P_int = int(P_post)
                # Converter para lista e remover duplicatas explicitamente
                camadas = list(dict.fromkeys(
                    MotorConfiguration.get_camadas_disponiveis(S_int, P_int)
                ))
                form.fields['Camada'].choices = [
                    ('', '--- Selecione o tipo de camada ---')
                ] + [(str(c), str(c).capitalize()) for c in camadas]
            except:
                form.fields['Camada'].choices = [('', '--- Selecione o tipo de camada ---')]
                P_int = None  # ← Definir P_int como None se houver erro

        # -------- Tipo de g --------
        if S_post and P_post and Camada_post and S_int is not None and P_int is not None:  # ← Verificar se ambos existem
            try:
                gtypes = list(dict.fromkeys(
                    MotorConfiguration.get_g_types_disponiveis(
                        S_int, P_int, Camada_post
                    )
                ))
                form.fields['g_type'].choices = [
                    ('', '--- Selecione o tipo de ligação ---')
                ] + [(str(g), str(g)) for g in gtypes]
            except:
                form.fields['g_type'].choices = [('', '--- Selecione o tipo de ligação ---')]

        # -------- Passo y --------
        if S_post and P_post and Camada_post and g_type_post:
            configs = MotorConfiguration.objects.filter(
                S=S_int, P=P_int, Camada=Camada_post, g_type=g_type_post
            ).order_by('-zeta')

            passos = configs.values_list('y', flat=True).distinct()

            form.fields['y'].choices = [
                ('', '--- Selecione o passo da bobina ---')
            ] + [(str(v), f"Passo {v}") for v in passos]

        # ========================================
        # 🔍 Validar agora que os choices estão OK
        # ========================================
        if form.is_valid():
            S = int(form.cleaned_data['S'])
            P = int(form.cleaned_data['P'])
            Camada = form.cleaned_data['Camada']
            g_type = form.cleaned_data['g_type']
            y = int(form.cleaned_data['y'])

            try:
                config = MotorConfiguration.objects.get(
                    S=S, P=P, Camada=Camada, g_type=g_type, y=y
                )

                # ===============================
                # 🔍 Impressões no terminal
                # ===============================
                print("\n========== CONFIGURAÇÃO RECEBIDA ==========")
                print(f"1) Número de ranhuras (S): {S}")
                print(f"2) Número de polos (P): {P}")
                print(f"3) Tipo de camada: {Camada}")
                print(f"4) Tipo de ligação (g_type): {g_type}")
                print(f"5) Passo selecionado (y): {y}")
                print(f"6) Fator zeta: {config.zeta}")
                print(f"7) Número de bobinas / info: {config.n_bob_info}")
                print(f"8) Tensão selecionada (V): {form.cleaned_data['V']}")
                print(f"9) Potência selecionada (CV): {form.cleaned_data['potencia_cv']}")
                print(f"10) Diâmetro do núcleo (mm): {form.cleaned_data['diametro_mm']}")  
                print(f"11) Comprimento do núcleo (mm): {form.cleaned_data['comprimento_mm']}")  
                print("===========================================\n")
                print("===========================================\n")

                # ========================================
                # 📐 CÁLCULOS DE DIMENSIONAMENTO
                # ========================================
                
                # 1. Converter dimensões de mm para cm
                Di_mm = int(form.cleaned_data['diametro_mm'])
                L_mm = int(form.cleaned_data['comprimento_mm'])
                Di = Di_mm / 10  # Converter para cm
                L = L_mm / 10    # Converter para cm
                
                print("\n========== CONVERSÃO DE UNIDADES ==========")
                print(f"Diâmetro: {Di_mm} mm = {Di} cm")
                print(f"Comprimento: {L_mm} mm = {L} cm")
                print("===========================================\n")
                
                # 2. Calcular tp (passo polar)
                tp = (3.14 * Di) / P
                print("========== CÁLCULO DO PASSO POLAR (tp) ==========")
                print(f"Equação: tp = (3.14 × Di) / P")
                print(f"tp = (3.14 × {Di}) / {P}")
                print(f"tp = {tp:.4f} cm")
                print("=================================================\n")
                
                # 3. Calcular fluxo magnético (fi)
                fi = (5 * tp * L) / 1000
                print("========== CÁLCULO DO FLUXO MAGNÉTICO (Φ) ==========")
                print(f"Equação: Φ = (5000 × tp × L) / 1000")
                print(f"Φ = (5 × {tp:.4f} × {L}) / 1000")
                print(f"Φ = {fi:.4f} Wb (Weber)")
                print("====================================================\n")
                
                # 4. Verificar ligações paralelas possíveis
                print("========== VERIFICAÇÃO DE LIGAÇÕES PARALELAS ==========")
                
                # Calcular número de grupos
                if g_type == 'g=P':
                    num_grupos = P
                    print(f"Tipo de ligação: g=P")
                else:  # g=P/2
                    num_grupos = P // 2
                    print(f"Tipo de ligação: g=P/2")
                
                print(f"Número de grupos: {num_grupos}")
                
                # Verificar divisibilidade
                k1_opcoes = [1]  # k1=1 sempre é possível
                
                if num_grupos % 2 == 0:
                    k1_opcoes.append(2)
                    print(f"✓ Divisível por 2: {num_grupos}/2 = {num_grupos//2} (k1=2 possível)")
                else:
                    print(f"✗ Não divisível por 2 (k1=2 não possível)")
                
                if num_grupos % 3 == 0:
                    k1_opcoes.append(3)
                    print(f"✓ Divisível por 3: {num_grupos}/3 = {num_grupos//3} (k1=3 possível)")
                else:
                    print(f"✗ Não divisível por 3 (k1=3 não possível)")

                if num_grupos % 4 == 0:
                    k1_opcoes.append(4)
                    print(f"✓ Divisível por 4: {num_grupos}/4 = {num_grupos//4} (k1=4 possível)")
                else:
                    print(f"✗ Não divisível por 4 (k1=4 não possível)")
                
                print(f"\nLigações paralelas possíveis (k1): {' ou '.join(map(str, k1_opcoes))}")
                print("=======================================================\n")
                
                # 5. Verificar coeficiente K (camada)
                if Camada == 'única':
                    k = 1
                else:  # dupla
                    k = 2
                
                print("========== COEFICIENTE DE CAMADA (k) ==========")
                print(f"Tipo de camada: {Camada}")
                print(f"Coeficiente k = {k}")
                print("===============================================\n")
                
                # 6. Identificar tensão para cálculo
                tensao_string = form.cleaned_data['V']
                if tensao_string == '220':
                    V = 220
                    rede = "220/380 V"
                elif tensao_string == '380':
                    V = 380
                    rede = "380/660 V"
                else:  # 440
                    V = 440
                    rede = "440/760 V"
                
                print("========== TENSÃO SELECIONADA ==========")
                print(f"Rede: {rede}")
                print(f"Tensão de fase (V) = {V} V")
                print("========================================\n")
                
                # 7. Calcular número de espiras por fase (ZF) para cada k1
                zeta_valor = float(config.zeta)
                
                print("========== CÁLCULO DE ESPIRAS POR FASE (ZF) ==========")
                print(f"Equação: ZF = (50 × V × k × k1) / (2.22 × Φ × 60 × ζ)")
                print(f"Valores: V={V}, k={k}, Φ={fi:.4f}, ζ={zeta_valor}")
                print()
                
                resultados_zf = {}
                ZF_resultados = {}
                for k1 in k1_opcoes:
                    print("======================================================\n")
                    ZF = (50 * V * k * k1) / (2.22 * fi * 60 * zeta_valor)
                    ZF_resultados[k1] = ZF
                    print(f"Para k1 = {k1} (ligação paralela {k1}):")
                    print(f"  ZF = (50 × {V} × {k} × {k1}) / (2.22 × {fi:.4f} × 60 × {zeta_valor})")
                    print(f"  ZF = {ZF:.2f} espiras por fase")
                    # 8. Calcular número de espiras por bobina (Z)
                    print(" Calculo de espiras por bobina:")
                    print(f"  S = {S:.2f} ranhuras")
                    print(f"Equação: Z = (3 × ZF) / S")
                    Z = round((3 * ZF) / S)
                    print(f"Espíras por bobina = {Z:.2f}")
                    print()
                    print(" Potência considerada para calculo da corrente com FP = 0.9 e Rend=0.9:")
                    Pot_cv = float(form.cleaned_data['potencia_cv'])
                    Pot = ((Pot_cv)/(0.9*0.9))*736 
                    print(f"  Potência considerada = {Pot:.2f} whats")
                    print(" Calculo de corrente de fase:")
                    I = Pot/(3*V)
                    print(f"  I = {I:.2f} ampéres")
                    print(" Calculo da área A do fio considerando I/densidade:")
                    if Pot_cv <= 10 :
                        d=7
                        print(f"  d = {d:.2f} ampéres/mm2")
                    elif Pot_cv <= 50 :
                        d=5.5
                        print(f"  d = {d:.2f} ampéres/mm2")
                    else:
                        d=5
                        print(f"  d = {d:.2f} ampéres/mm2")
                    A = I/(d*k1)
                    print(f"  Utilize fio = {A:.3f} mm2")
                    awg_sugerido = get_awg_for_area(A, mode='next_larger')
                    if awg_sugerido:
                        print(f"  Sugestão: {awg_sugerido['descricao']} (área: {awg_sugerido['area_mm2']:.3f} mm²)")
                    else:
                        print(f"  Área {A:.3f} mm² fora da faixa. Consulte tabela manual.")
                    print()

                    # Armazenar resultado
                    resultados_zf[k1] = {
                        'zf': round(ZF, 2),
                        'z': Z,
                        'awg': awg_sugerido
                    }
                
                print("======================================================\n")
                
                g_type_descricao = "fim com fim" if g_type == "g=P" else "fim com início"
                # Estruturar opções de construção
                opcoes_construcao = []

                # Para cada k1 calculado, criar uma opção
                for idx, k1 in enumerate(k1_opcoes, 1):
                    # Buscar os dados calculados para este k1
                    ZF = resultados_zf[k1]['zf']
                    Z = resultados_zf[k1]['z']
                    awg_completo = resultados_zf[k1]['awg']
                    
                    if isinstance(awg_completo, dict):
                        awg_bitola = str(awg_completo.get('awg', awg_completo.get('descricao', '18')))
                    else:
                        # Se for string ou número
                        awg_str = str(awg_completo)
                        
                        # Remover informações entre parênteses se existir
                        if '(' in awg_str:
                            awg_bitola = awg_str.split('(')[0]
                        else:
                            awg_bitola = awg_str
                        
                        # Remover " AWG" se existir
                        awg_bitola = awg_bitola.replace(' AWG', '').replace('AWG', '').strip()
                    
                    # Calcular número de grupos em série e paralelo
                    grupos_serie = num_grupos // k1
                    grupos_paralelo = k1
                    
                    # Extrair informação de bobinas por grupo
                    bobinas_por_grupo = config.n_bob_info
                    
                    opcao = {
                        'numero': idx,
                        'k1': k1,
                        'grupos_total': num_grupos,
                        'grupos_serie': grupos_serie,
                        'grupos_paralelo': grupos_paralelo,
                        'bobinas_por_grupo': bobinas_por_grupo,
                        'passo': y,
                        'espiras_por_bobina': Z,
                        'espiras_por_fase': ZF,
                        'fio_awg': awg_bitola,
                        'g_type': g_type,
                        'g_type_descricao': g_type_descricao,
                        'camada': Camada,
                        'descricao': ''
                    }
                    
                    # Criar descrição personalizada
                    if k1 == 1:
                        opcao['descricao'] = (
                            f"Todos os grupos ligados em série. "
                            f"Realize a bobinagem montando {num_grupos} grupos, "
                            f"cada grupo com {bobinas_por_grupo} bobinas, "
                            f"utilizando passo polar 1:{y+1}. "
                            f"Cada bobina implemente com {Z} espiras "
                            f"com fio {awg_bitola} AWG. "
                            f"Implemente ligação do tipo {g_type_descricao}."
                        )
                    else:
                        opcao['descricao'] = (
                            f"Para cada fase, ligue {grupos_serie} grupos em série "
                            f"e cada conjunto conecte em paralelo ({k1} circuitos paralelos). "
                            f"Realize a bobinagem montando {num_grupos} grupos, "
                            f"cada grupo com {bobinas_por_grupo} bobinas, "
                            f"utilizando passo polar 1:{y+1}. "
                            f"Cada bobina implemente com {Z} espiras "
                            f"com fio {awg_bitola} AWG. "
                            f"Implemente ligação do tipo {g_type_descricao}."
                        )
                    
                    opcoes_construcao.append(opcao)

                # ========================================
                # 📊 PREPARAR CONTEXTO COMPLETO
                # ========================================

                contexto = {
                    'form': form,
                    'mensagem': 'Cálculo realizado com sucesso!',
                    'configuracao': {
                        'S': S,
                        'P': P,
                        'Camada': Camada,
                        'g_type': g_type,
                        'y': y,
                        'zeta': float(config.zeta),
                        'n_bobinas': config.n_bob_info,
                        'V': V,
                        'potencia_cv': form.cleaned_data['potencia_cv'],
                        'diametro_mm': Di_mm,
                        'comprimento_mm': L_mm,
                    },
                    'calculos': {
                        'tp': round(tp, 4),
                        'fluxo': round(fi, 4),
                        'num_grupos': num_grupos,
                    },
                    'opcoes_construcao': opcoes_construcao,
                    'resultados_calculados': True
                }

                return render(request, 'calculo_espiras.html', contexto)

            except MotorConfiguration.DoesNotExist:
                print("\n❌ Configuração NÃO encontrada no banco!\n")
                return render(request, "calculo_espiras.html", {
                    "form": form,
                    "erro": "Configuração não encontrada no banco."
                })


        else:
            print("❌ Formulário inválido (POST)")
            print(form.errors)

        return render(request, "calculo_espiras.html", {"form": form})

    # ========================================
    # GET → apenas formulário inicial
    # ========================================
    else:
        form = ConfiguracaoMotorForm()
        return render(request, "calculo_espiras.html", {"form": form})



# =============================================================================
# APIS AJAX PARA CARREGAR OPÇÕES DINAMICAMENTE
# =============================================================================

@require_http_methods(["GET"])
def api_get_polos(request):
    """
    API para obter polos disponíveis para um número de ranhuras.
    
    Parâmetros:
        - S (int): Número de ranhuras
        
    Retorna:
        JSON com lista de polos disponíveis
    """
    S = request.GET.get('S')
    
    if not S:
        return JsonResponse({'erro': 'Parâmetro S obrigatório'}, status=400)
    
    try:
        S = int(S)
        polos = list(MotorConfiguration.get_polos_disponiveis(S))
        
        return JsonResponse({
            'polos': [
                {'value': p, 'label': f'{p} polos'}
                for p in polos
            ]
        })
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@require_http_methods(["GET"])
def api_get_camadas(request):
    """
    API para obter camadas disponíveis e a recomendação baseada na potência.
    
    Parâmetros:
        - S (int): Número de ranhuras
        - P (int): Número de polos
        - potencia_cv (float, opcional): Potência para recomendação
        
    Retorna:
        JSON com lista de camadas e recomendação
    """
    S = request.GET.get('S')
    P = request.GET.get('P')
    potencia_cv = request.GET.get('potencia_cv', 5)  # Default: 5 CV
    
    if not S or not P:
        return JsonResponse({'erro': 'Parâmetros S e P obrigatórios'}, status=400)
    
    try:
        S = int(S)
        P = int(P)
        potencia_cv = float(potencia_cv)
        
        # Obter camadas disponíveis
        camadas = list(MotorConfiguration.get_camadas_disponiveis(S, P))
        
        # Obter sugestão baseada na potência
        camada_sugerida = MotorConfiguration.sugerir_camada(S, P, potencia_cv)
        
        return JsonResponse({
            'camadas': [
                {
                    'value': c,
                    'label': f'Camada {c}',
                    'recomendada': c == camada_sugerida
                }
                for c in camadas
            ],
            'recomendacao': {
                'camada': camada_sugerida,
                'motivo': f'Recomendado para motores {"≤ 5 CV" if potencia_cv <= 5 else "> 5 CV"}'
            }
        })
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@require_http_methods(["GET"])
def api_get_g_types(request):
    """
    API para obter tipos de g disponíveis e a recomendação baseada na potência.
    
    Parâmetros:
        - S (int): Número de ranhuras
        - P (int): Número de polos
        - Camada (str): Tipo de camada
        - potencia_cv (float, opcional): Potência para recomendação
        
    Retorna:
        JSON com lista de g_types e recomendação
    """
    S = request.GET.get('S')
    P = request.GET.get('P')
    Camada = request.GET.get('Camada')
    potencia_cv = request.GET.get('potencia_cv', 5)  # Default: 5 CV
    
    if not S or not P or not Camada:
        return JsonResponse({'erro': 'Parâmetros S, P e Camada obrigatórios'}, status=400)
    
    try:
        S = int(S)
        P = int(P)
        potencia_cv = float(potencia_cv)
        
        # Obter g_types disponíveis
        g_types = list(MotorConfiguration.get_g_types_disponiveis(S, P, Camada))
        
        # Obter sugestão baseada na potência
        g_type_sugerido = MotorConfiguration.sugerir_g_type(S, P, Camada, potencia_cv)
        
        # Mapear labels amigáveis
        label_map = {
            'g=P': 'g=P (ligação fim com fim)',
            'g=P/2': 'g=P/2 (ligação fim com início)'
        }
        
        return JsonResponse({
            'g_types': [
                {
                    'value': g,
                    'label': label_map.get(g, g),
                    'recomendada': g == g_type_sugerido
                }
                for g in g_types
            ],
            'recomendacao': {
                'g_type': g_type_sugerido,
                'motivo': f'Recomendado para motores {"≤ 3 CV" if potencia_cv <= 3 else "> 3 CV"}'
            }
        })
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@require_http_methods(["GET"])
def api_get_passos(request):
    """
    API para obter passos disponíveis e identificar o recomendado.
    
    Parâmetros:
        - S (int): Número de ranhuras
        - P (int): Número de polos
        - Camada (str): Tipo de camada
        - g_type (str): Tipo de g
        
    Retorna:
        JSON com lista de passos, zeta e número de bobinas
    """
    S = request.GET.get('S')
    P = request.GET.get('P')
    Camada = request.GET.get('Camada')
    g_type = request.GET.get('g_type')
    
    if not all([S, P, Camada, g_type]):
        return JsonResponse({
            'erro': 'Parâmetros S, P, Camada e g_type obrigatórios'
        }, status=400)
    
    try:
        S = int(S)
        P = int(P)
        
        # Buscar todas as configurações possíveis
        configs = MotorConfiguration.objects.filter(
            S=S,
            P=P,
            Camada=Camada,
            g_type=g_type
        ).order_by('-zeta')  # Ordenar por melhor zeta
        
        if not configs.exists():
            return JsonResponse({
                'erro': 'Nenhuma configuração encontrada com esses parâmetros'
            }, status=404)
        
        # Montar lista de passos
        passos = []
        for config in configs:
            passos.append({
                'value': config.y,
                'label': f'Passo {config.y} (ζ={config.zeta})',
                'zeta': float(config.zeta),
                'n_bobinas': config.n_bob_info,
                'classificacao': config.Classificacao_zeta,
                'recomendado': config.Observacao_passo == 'recomendado'
            })
        
        # Identificar o passo recomendado
        passo_recomendado = next(
            (p for p in passos if p['recomendado']), 
            passos[0]  # Se nenhum marcado, usar o primeiro (melhor zeta)
        )
        
        return JsonResponse({
            'passos': passos,
            'recomendacao': {
                'passo': passo_recomendado['value'],
                'zeta': passo_recomendado['zeta'],
                'motivo': f'Melhor fator de enrolamento (ζ={passo_recomendado["zeta"]})'
            }
        })
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)


@require_http_methods(["GET"])
def api_get_info_configuracao(request):
    """
    API para obter informações completas de uma configuração específica.
    Usado quando o usuário seleciona o passo final.
    
    Parâmetros:
        - S, P, Camada, g_type, y
        
    Retorna:
        JSON com zeta, n_bobinas e outras informações
    """
    S = request.GET.get('S')
    P = request.GET.get('P')
    Camada = request.GET.get('Camada')
    g_type = request.GET.get('g_type')
    y = request.GET.get('y')
    
    if not all([S, P, Camada, g_type, y]):
        return JsonResponse({
            'erro': 'Todos os parâmetros são obrigatórios'
        }, status=400)
    
    try:
        config = MotorConfiguration.objects.get(
            S=int(S),
            P=int(P),
            Camada=Camada,
            g_type=g_type,
            y=int(y)
        )
        
        return JsonResponse({
            'zeta': float(config.zeta),
            'n_bobinas': config.n_bob_info,
            'q': float(config.q),
            'tipo_q': config.tipo_q,
            'classificacao': config.Classificacao_zeta,
            'observacao': config.Observacao_passo,
            'recomendado': config.is_recomendado()
        })
    except MotorConfiguration.DoesNotExist:
        return JsonResponse({
            'erro': 'Configuração não encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)