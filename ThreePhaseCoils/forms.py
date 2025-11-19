from django import forms


class ConfiguracaoMotorForm(forms.Form):
    """
    Formulário dinâmico para configuração de motor.
    Os campos são preenchidos via AJAX conforme o usuário faz escolhas.
    """
    
    # 1. NÚMERO DE RANHURAS (primeiro campo - carregado do banco)
    S = forms.ChoiceField(
        label='Número de Ranhuras (S)',
        choices=[],  # Será populado dinamicamente
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'ranhuras-select'
        }),
        help_text='Selecione o número de ranhuras do motor'
    )
    
    # 2. NÚMERO DE POLOS (carregado via AJAX após selecionar ranhuras)
    P = forms.ChoiceField(
        label='Número de Polos (P)',
        choices=[],  # Será populado via AJAX
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'polos-select',
            'disabled': 'disabled'
        }),
        help_text='Selecione o número de polos (carregado após selecionar ranhuras)'
    )
    
    # 3. TIPO DE CAMADA (carregado via AJAX após selecionar polos)
    Camada = forms.ChoiceField(
        label='Tipo de Camada',
        choices=[],  # Será populado via AJAX
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'camada-select',
            'disabled': 'disabled'
        }),
        help_text='Tipo de bobinagem (a recomendação será indicada)'
    )
    
    # 4. TIPO DE G (carregado via AJAX após selecionar camada)
    g_type = forms.ChoiceField(
        label='Tipo de Ligação',
        choices=[],  # Será populado via AJAX
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'g-type-select',
            'disabled': 'disabled'
        }),
        help_text='Tipo de ligação: g=P (fim com fim) ou g=P/2 (fim com início)'
    )
    
    # 5. PASSO DA BOBINA (carregado via AJAX após selecionar g_type)
    y = forms.ChoiceField(
        label='Passo da Bobina (y)',
        choices=[],  # Será populado via AJAX
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'passo-select',
            'disabled': 'disabled'
        }),
        help_text='Passo da bobinagem (o passo recomendado será indicado)'
    )
    
    # 6. TENSÃO (sempre disponível - não depende de AJAX)
    V = forms.ChoiceField(
        label='Tensão de Fase (V)',
        choices=[
            ('220', '220 V (rede 220/380 V)'),
            ('380', '380 V (rede 380/660 V)'),
            ('440', '440 V (rede 440/760 V)'),
        ],
        initial='380',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'tensao-select'
        }),
        help_text='Tensão de fase do motor'
    )
    
    # 7. POTÊNCIA (sempre disponível - não depende de AJAX)
    potencia_cv = forms.ChoiceField(
        label='Potência do Motor (CV)',
        choices=[
            ('0.12', '0,12 CV - 1/8 CV - 0,088 kW'),
            ('0.16', '0,16 CV - 1/6 CV - 0,118 kW'),
            ('0.18', '0,18 CV - 0,132 kW'),
            ('0.25', '0,25 CV - 1/4 CV - 0,184 kW'),
            ('0.33', '0,33 CV - 1/3 CV - 0,243 kW'),
            ('0.37', '0,37 CV - 0,272 kW'),
            ('0.50', '0,50 CV - 1/2 CV - 0,368 kW'),
            ('0.55', '0,55 CV - 0,404 kW'),
            ('0.75', '0,75 CV - 3/4 CV - 0,552 kW'),
            ('0.84', '0,84 CV - 0,618 kW'),
            ('0.92', '0,92 CV - 0,677 kW'),
            ('1', '1 CV - 0,736 kW'),
            ('1.5', '1,5 CV - 1,103 kW'),
            ('2', '2 CV - 1,471 kW'),
            ('2.2', '2,2 CV - 1,618 kW'),
            ('3', '3 CV - 2,207 kW'),
            ('3.7', '3,7 CV - 2,721 kW'),
            ('4', '4 CV - 2,942 kW'),
            ('4.5', '4,5 CV - 3,310 kW'),
            ('5', '5 CV - 3,678 kW'),
            ('5.5', '5,5 CV - 4,045 kW'),
            ('6', '6 CV - 4,413 kW'),
            ('7.5', '7,5 CV - 5,516 kW'),
            ('9.2', '9,2 CV - 6,767 kW'),
            ('10', '10 CV - 7,355 kW'),
            ('11', '11 CV - 8,091 kW'),
            ('12.5', '12,5 CV - 9,194 kW'),
            ('15', '15 CV - 11,033 kW'),
            ('18.5', '18,5 CV - 13,607 kW'),
            ('20', '20 CV - 14,710 kW'),
            ('22', '22 CV - 16,181 kW'),
            ('25', '25 CV - 18,388 kW'),
            ('30', '30 CV - 22,065 kW'),
            ('37', '37 CV - 27,214 kW'),
            ('40', '40 CV - 29,420 kW'),
            ('45', '45 CV - 33,098 kW'),
            ('50', '50 CV - 36,775 kW'),
            ('55', '55 CV - 40,453 kW'),
            ('60', '60 CV - 44,130 kW'),
            ('75', '75 CV - 55,163 kW'),
            ('90', '90 CV - 66,195 kW'),
            ('100', '100 CV - 73,550 kW'),
            ('110', '110 CV - 80,905 kW'),
            ('125', '125 CV - 91,938 kW'),
            ('132', '132 CV - 97,086 kW'),
            ('150', '150 CV - 110,325 kW'),
            ('160', '160 CV - 117,680 kW'),
            ('175', '175 CV - 128,713 kW'),
            ('185', '185 CV - 136,068 kW'),
            ('200', '200 CV - 147,100 kW'),
            ('220', '220 CV - 161,810 kW'),
            ('225', '225 CV - 165,488 kW'),
            ('250', '250 CV - 183,875 kW'),
            ('260', '260 CV - 191,230 kW'),
            ('270', '270 CV - 198,585 kW'),
            ('280', '280 CV - 205,940 kW'),
            ('300', '300 CV - 220,650 kW'),
            ('315', '315 CV - 231,683 kW'),
            ('330', '330 CV - 242,715 kW'),
            ('350', '350 CV - 257,425 kW'),
            ('370', '370 CV - 272,135 kW'),
            ('400', '400 CV - 294,200 kW'),
            ('450', '450 CV - 330,975 kW'),
            ('500', '500 CV - 367,750 kW'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'potencia-select'
        }),
        help_text='Potência nominal do motor'
    )

    # 8. DIÂMETRO (sempre disponível - não depende de AJAX)
    diametro_mm = forms.IntegerField(
        label='Diâmetro do Núcleo (mm)',
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'diametro-input',
            'min': '1',
            'placeholder': 'Digite o diâmetro em mm'
        }),
        help_text='Diâmetro do núcleo condutor em milímetros'
    )
    
    # 9. COMPRIMENTO (sempre disponível - não depende de AJAX)
    comprimento_mm = forms.IntegerField(
        label='Comprimento do Núcleo (mm)',
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'comprimento-input',
            'min': '1',
            'placeholder': 'Digite o comprimento do núcleo em mm'
        }),
        help_text='Comprimento do núcleo condutor em milímetros'
    )
    
    def __init__(self, *args, **kwargs):
        """
        Inicializa o formulário e carrega as opções de ranhuras do banco de dados.
        """
        super().__init__(*args, **kwargs)
        
        # Importar aqui para evitar circular imports
        from ThreePhaseCoils.models import MotorConfiguration
        
        # Carregar ranhuras disponíveis do banco de dados
        ranhuras_disponiveis = MotorConfiguration.objects.values_list(
            'S', flat=True
        ).distinct().order_by('S')
        
        # Criar choices para o campo de ranhuras
        self.fields['S'].choices = [
            ('', '--- Selecione o número de ranhuras ---')
        ] + [(str(s), f'{s} ranhuras') for s in ranhuras_disponiveis]