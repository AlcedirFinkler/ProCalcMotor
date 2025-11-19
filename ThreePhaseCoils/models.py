from django.db import models
from django.core.validators import MinValueValidator


class MotorConfiguration(models.Model):
    """
    Modelo para armazenar configurações válidas de bobinagem de motores trifásicos de indução.
    
    Cada registro representa uma combinação válida de parâmetros que pode ser usada
    no projeto de um motor elétrico trifásico.
    """
    
    # Choices para campos categóricos
    G_TYPE_CHOICES = [
        ('g=P', 'g=P'),
        ('g=P/2', 'g=P/2'),
    ]
    
    CAMADA_CHOICES = [
        ('única', 'Camada Única'),
        ('dupla', 'Camada Dupla'),
    ]
    
    TIPO_Q_CHOICES = [
        ('inteiro', 'Inteiro'),
        ('fracionário', 'Fracionário'),
    ]
    
    CLASSIFICACAO_CHOICES = [
        ('excelente', 'Excelente'),
        ('bom', 'Bom'),
        ('aceitável', 'Aceitável'),
        ('evitar', 'Evitar'),
    ]
    
    # Campos principais
    S = models.IntegerField(
        verbose_name='Número de Ranhuras',
        help_text='Número de ranhuras do estator (slots)',
        validators=[MinValueValidator(1)]
    )
    
    P = models.IntegerField(
        verbose_name='Número de Polos',
        help_text='Número de polos do motor',
        validators=[MinValueValidator(2)]
    )
    
    g_type = models.CharField(
        max_length=10,
        choices=G_TYPE_CHOICES,
        verbose_name='Tipo de g',
        help_text='Configuração do número de grupos'
    )
    
    Camada = models.CharField(
        max_length=10,
        choices=CAMADA_CHOICES,
        verbose_name='Tipo de Camada',
        help_text='Configuração de camada única ou dupla'
    )
    
    q = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Valor de q',
        help_text='Número de ranhuras por polo por fase',
        validators=[MinValueValidator(0)]
    )
    
    tipo_q = models.CharField(
        max_length=15,
        choices=TIPO_Q_CHOICES,
        verbose_name='Tipo de q',
        help_text='Indica se q é inteiro ou fracionário'
    )
    
    n_bob_info = models.CharField(
        max_length=50,
        verbose_name='Informação de Bobinas',
        help_text='Número de bobinas ou distribuição por grupo'
    )
    
    y = models.IntegerField(
        verbose_name='Passo Polar',
        help_text='Passo de bobinagem',
        validators=[MinValueValidator(1)]
    )
    
    zeta = models.DecimalField(
        max_digits=6,
        decimal_places=4,
        verbose_name='Fator Zeta',
        help_text='Fator de distribuição de enrolamento',
        validators=[MinValueValidator(0)]
    )
    
    Classificacao_zeta = models.CharField(
        max_length=15,
        choices=CLASSIFICACAO_CHOICES,
        verbose_name='Classificação',
        help_text='Classificação da qualidade da configuração'
    )
    
    Observacao_passo = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name='Observação',
        help_text='Observações sobre a recomendação do passo'
    )
    
    # Campos de controle
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    
    class Meta:
        verbose_name = 'Configuração de Motor'
        verbose_name_plural = 'Configurações de Motores'
        ordering = ['S', 'P', 'g_type', 'Camada', 'y']
        
        # Índices para otimizar consultas comuns
        indexes = [
            models.Index(fields=['S'], name='idx_ranhuras'),
            models.Index(fields=['S', 'P'], name='idx_ranhuras_polos'),
            models.Index(fields=['S', 'P', 'Camada'], name='idx_ranhuras_polos_camada'),
            models.Index(fields=['S', 'P', 'g_type'], name='idx_ranhuras_polos_gtype'),
            models.Index(fields=['Classificacao_zeta'], name='idx_classificacao'),
        ]
        
        # Constraint para evitar duplicatas
        unique_together = ['S', 'P', 'g_type', 'Camada', 'y']
    
    def __str__(self):
        return f"S={self.S}, P={self.P}, {self.g_type}, {self.Camada}, y={self.y}"
    
    # Métodos úteis para consultas
    
    @classmethod
    def get_camadas_disponiveis(cls, S, P):
        return list(cls.objects.filter(
            S=S, P=P
        ).values_list('Camada', flat=True).distinct().order_by('Camada'))

    @classmethod
    def get_g_types_disponiveis(cls, S, P, Camada):
        return list(cls.objects.filter(
            S=S, 
            P=P, 
            Camada=Camada
        ).values_list('g_type', flat=True).distinct().order_by('g_type'))
    
    @classmethod
    def get_polos_disponiveis(cls, S):
        """
        Retorna lista de polos disponíveis para um número de ranhuras S.
        """
        return cls.objects.filter(S=S)\
                .values_list('P', flat=True)\
                .distinct()\
                .order_by('P')
    
    @classmethod
    def get_configuracoes_recomendadas(cls, S, P, Camada=None, g_type=None):
        """
        Retorna configurações recomendadas ou com classificação 'excelente'.
        
        Args:
            S (int): Número de ranhuras
            P (int): Número de polos
            Camada (str, optional): Tipo de camada
            g_type (str, optional): Tipo de g
            
        Returns:
            QuerySet: Configurações recomendadas
        """
        filters = {'S': S, 'P': P}
        
        if Camada:
            filters['Camada'] = Camada
        
        if g_type:
            filters['g_type'] = g_type
        
        return cls.objects.filter(
            **filters,
            Classificacao_zeta__in=['excelente', 'bom']
        ).order_by('-zeta')
    
    @classmethod
    def get_melhor_configuracao(cls, S, P, Camada, g_type):
        """
        Retorna a melhor configuração (maior zeta) para os parâmetros dados.
        
        Args:
            S (int): Número de ranhuras
            P (int): Número de polos
            Camada (str): Tipo de camada
            g_type (str): Tipo de g
            
        Returns:
            MotorConfiguration ou None: Melhor configuração encontrada
        """
        return cls.objects.filter(
            S=S,
            P=P,
            Camada=Camada,
            g_type=g_type
        ).order_by('-zeta').first()
    
    @classmethod
    def sugerir_camada(cls, S, P, potencia_cv):
        """
        Sugere o tipo de camada baseado na potência do motor.
        
        Args:
            S (int): Número de ranhuras
            P (int): Número de polos
            potencia_cv (float): Potência em CV
            
        Returns:
            str: Tipo de camada sugerido ('única' ou 'dupla')
        """
        camadas_disponiveis = list(cls.get_camadas_disponiveis(S, P))
        
        if potencia_cv <= 5:
            # Para motores ≤ 5CV, prefere camada única
            if 'única' in camadas_disponiveis:
                return 'única'
        else:
            # Para motores > 5CV, prefere camada dupla
            if 'dupla' in camadas_disponiveis:
                return 'dupla'
        
        # Retorna a primeira disponível se a preferida não existir
        return camadas_disponiveis[0] if camadas_disponiveis else None
    
    @classmethod
    def sugerir_g_type(cls, S, P, Camada, potencia_cv):
        """
        Sugere o tipo de g baseado na potência do motor.
        
        Args:
            S (int): Número de ranhuras
            P (int): Número de polos
            Camada (str): Tipo de camada
            potencia_cv (float): Potência em CV
            
        Returns:
            str: Tipo de g sugerido ('g=P' ou 'g=P/2')
        """
        g_types_disponiveis = list(cls.get_g_types_disponiveis(S, P, Camada))
        
        if potencia_cv <= 3:
            # Para motores ≤ 3CV, prefere g=P/2
            if 'g=P/2' in g_types_disponiveis:
                return 'g=P/2'
        else:
            # Para motores > 3CV, prefere g=P
            if 'g=P' in g_types_disponiveis:
                return 'g=P'
        
        # Retorna a primeira disponível se a preferida não existir
        return g_types_disponiveis[0] if g_types_disponiveis else None
    
    def is_recomendado(self):
        """Verifica se esta configuração é recomendada."""
        return self.Observacao_passo == 'recomendado'
    
    def is_excelente(self):
        """Verifica se esta configuração tem classificação excelente."""
        return self.Classificacao_zeta == 'excelente'
    
    def get_rpm_sincrona(self, frequencia=60):
        """
        Calcula a rotação síncrona do motor.
        
        Args:
            frequencia (int): Frequência da rede em Hz (padrão: 60Hz)
            
        Returns:
            int: RPM síncrona
        """
        return int((120 * frequencia) / self.P)