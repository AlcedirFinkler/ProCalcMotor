# analytics/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class AccessLog(models.Model):
    """
    Modelo para registrar todos os acessos ao site com informações geográficas
    """
    # Informações temporais
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    date = models.DateField(auto_now_add=True, db_index=True)
    
    # Informações da requisição
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500, blank=True)
    path = models.CharField(max_length=200)
    
    # Informações geográficas
    country = models.CharField(max_length=100, blank=True, default='Brasil')
    country_code = models.CharField(max_length=10, blank=True, default='BR')
    state = models.CharField(max_length=100, blank=True, db_index=True)
    state_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True, db_index=True)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    
    # Informações do ISP
    isp = models.CharField(max_length=200, blank=True)
    organization = models.CharField(max_length=200, blank=True)
    
    # Tipo de acesso
    access_type = models.CharField(
        max_length=50,
        choices=[
            ('page_view', 'Visualização de Página'),
            ('calculation', 'Cálculo Realizado'),
            ('download', 'Download'),
            ('form_submit', 'Formulário Enviado')
        ],
        default='page_view'
    )
    
    # Detalhes específicos do cálculo (se aplicável)
    calculation_type = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('potencia', 'Cálculo de Potência'),
            ('espiras', 'Cálculo de Espiras'),
            ('diagrama', 'Geração de Diagrama'),
        ]
    )
    
    # Usuário autenticado (se aplicável)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadados adicionais
    session_key = models.CharField(max_length=100, blank=True)
    referer = models.URLField(max_length=500, blank=True)
    is_mobile = models.BooleanField(default=False)
    is_bot = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'state', 'city']),
            models.Index(fields=['date', 'access_type']),
        ]
    
    def __str__(self):
        return f"{self.city}/{self.state} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def location_display(self):
        """Retorna localização formatada"""
        parts = []
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.country and self.country != 'Brasil':
            parts.append(self.country)
        return ', '.join(parts) if parts else 'Localização Desconhecida'


class DailyStatsSummary(models.Model):
    """
    Modelo para armazenar estatísticas diárias agregadas (otimização de performance)
    """
    date = models.DateField(unique=True, db_index=True)
    
    # Totais gerais
    total_visits = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    total_calculations = models.IntegerField(default=0)
    
    # Por tipo de cálculo
    potencia_calculations = models.IntegerField(default=0)
    espiras_calculations = models.IntegerField(default=0)
    diagrama_calculations = models.IntegerField(default=0)
    
    # Estatísticas geográficas (JSON com contadores por estado/cidade)
    geographic_data = models.JSONField(default=dict)
    
    # Top locations
    top_states = models.JSONField(default=list)  # Lista dos 5 estados mais acessados
    top_cities = models.JSONField(default=list)   # Lista das 10 cidades mais acessadas
    
    # Dispositivos
    mobile_visits = models.IntegerField(default=0)
    desktop_visits = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Resumo Diário de Estatísticas'
        verbose_name_plural = 'Resumos Diários de Estatísticas'
        ordering = ['-date']
    
    def __str__(self):
        return f"Estatísticas de {self.date.strftime('%d/%m/%Y')}"


class GeographicRegion(models.Model):
    """
    Modelo para armazenar informações sobre regiões geográficas do Brasil
    """
    REGIONS = [
        ('norte', 'Norte'),
        ('nordeste', 'Nordeste'),
        ('centro-oeste', 'Centro-Oeste'),
        ('sudeste', 'Sudeste'),
        ('sul', 'Sul'),
    ]
    
    state_name = models.CharField(max_length=100, unique=True)
    state_code = models.CharField(max_length=2, unique=True)
    region = models.CharField(max_length=20, choices=REGIONS)
    population = models.IntegerField(null=True, blank=True)
    
    # Coordenadas do centro do estado (para o mapa)
    center_latitude = models.DecimalField(max_digits=10, decimal_places=6)
    center_longitude = models.DecimalField(max_digits=10, decimal_places=6)
    
    class Meta:
        verbose_name = 'Região Geográfica'
        verbose_name_plural = 'Regiões Geográficas'
        ordering = ['state_name']
    
    def __str__(self):
        return f"{self.state_name} ({self.state_code})"


# Estados brasileiros pré-configurados
BRAZILIAN_STATES = {
    'AC': {'name': 'Acre', 'region': 'norte', 'lat': -9.0238, 'lng': -70.8120},
    'AL': {'name': 'Alagoas', 'region': 'nordeste', 'lat': -9.5713, 'lng': -36.7820},
    'AP': {'name': 'Amapá', 'region': 'norte', 'lat': 0.9020, 'lng': -52.0030},
    'AM': {'name': 'Amazonas', 'region': 'norte', 'lat': -3.4168, 'lng': -65.8561},
    'BA': {'name': 'Bahia', 'region': 'nordeste', 'lat': -12.5797, 'lng': -41.7007},
    'CE': {'name': 'Ceará', 'region': 'nordeste', 'lat': -5.4984, 'lng': -39.3206},
    'DF': {'name': 'Distrito Federal', 'region': 'centro-oeste', 'lat': -15.7998, 'lng': -47.8645},
    'ES': {'name': 'Espírito Santo', 'region': 'sudeste', 'lat': -19.1834, 'lng': -40.3089},
    'GO': {'name': 'Goiás', 'region': 'centro-oeste', 'lat': -15.8270, 'lng': -49.8362},
    'MA': {'name': 'Maranhão', 'region': 'nordeste', 'lat': -4.9609, 'lng': -45.2744},
    'MT': {'name': 'Mato Grosso', 'region': 'centro-oeste', 'lat': -12.6819, 'lng': -56.9211},
    'MS': {'name': 'Mato Grosso do Sul', 'region': 'centro-oeste', 'lat': -20.7722, 'lng': -54.7852},
    'MG': {'name': 'Minas Gerais', 'region': 'sudeste', 'lat': -18.5122, 'lng': -44.5550},
    'PA': {'name': 'Pará', 'region': 'norte', 'lat': -1.9981, 'lng': -54.9306},
    'PB': {'name': 'Paraíba', 'region': 'nordeste', 'lat': -7.2399, 'lng': -36.7820},
    'PR': {'name': 'Paraná', 'region': 'sul', 'lat': -25.2521, 'lng': -52.0215},
    'PE': {'name': 'Pernambuco', 'region': 'nordeste', 'lat': -8.8137, 'lng': -36.9541},
    'PI': {'name': 'Piauí', 'region': 'nordeste', 'lat': -7.7183, 'lng': -42.7289},
    'RJ': {'name': 'Rio de Janeiro', 'region': 'sudeste', 'lat': -22.9068, 'lng': -43.1729},
    'RN': {'name': 'Rio Grande do Norte', 'region': 'nordeste', 'lat': -5.4026, 'lng': -36.9541},
    'RS': {'name': 'Rio Grande do Sul', 'region': 'sul', 'lat': -30.0346, 'lng': -51.2177},
    'RO': {'name': 'Rondônia', 'region': 'norte', 'lat': -11.5057, 'lng': -63.5806},
    'RR': {'name': 'Roraima', 'region': 'norte', 'lat': 1.9957, 'lng': -61.3330},
    'SC': {'name': 'Santa Catarina', 'region': 'sul', 'lat': -27.2423, 'lng': -50.2189},
    'SP': {'name': 'São Paulo', 'region': 'sudeste', 'lat': -23.5505, 'lng': -46.6333},
    'SE': {'name': 'Sergipe', 'region': 'nordeste', 'lat': -10.5741, 'lng': -37.3857},
    'TO': {'name': 'Tocantins', 'region': 'norte', 'lat': -10.1753, 'lng': -48.2982}
}