# analytics/middleware.py
import json
import requests
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.core.cache import cache
from .models import AccessLog
from user_agents import parse
import logging

logger = logging.getLogger(__name__)


class GeoLocationMiddleware(MiddlewareMixin):
    """
    Middleware para capturar informações de geolocalização de cada acesso
    """
    
    # URLs que devem ser ignoradas (admin, static files, etc)
    IGNORE_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
        '/favicon.ico',
        '/robots.txt',
        '/__debug__/',
    ]
    
    # IPs locais que devem ser ignorados ou tratados diferentemente
    LOCAL_IPS = ['127.0.0.1', 'localhost', '::1']
    
    def process_request(self, request):
        """
        Processa cada requisição e registra informações de geolocalização
        """
        try:
            # Ignora caminhos específicos
            if any(request.path.startswith(path) for path in self.IGNORE_PATHS):
                return None
            
            # Obtém o IP real do cliente
            ip_address = self.get_client_ip(request)
            
            # Se for desenvolvimento local, usa IP de teste
            if ip_address in self.LOCAL_IPS and settings.DEBUG:
                ip_address = '177.67.80.100'  # IP de teste (São Paulo)
            
            # Verifica se já temos dados em cache para este IP
            cache_key = f'geo_location_{ip_address}'
            geo_data = cache.get(cache_key)
            
            if not geo_data:
                # Busca dados de geolocalização
                geo_data = self.get_geolocation(ip_address)
                # Armazena em cache por 24 horas
                cache.set(cache_key, geo_data, 86400)
            
            # Detecta informações do dispositivo
            user_agent_string = request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(user_agent_string)
            is_mobile = user_agent.is_mobile
            is_bot = user_agent.is_bot
            
            # Cria registro de acesso
            access_log = AccessLog(
                ip_address=ip_address,
                user_agent=user_agent_string[:500],
                path=request.path,
                is_mobile=is_mobile,
                is_bot=is_bot,
                session_key=request.session.session_key if hasattr(request, 'session') else '',
                referer=request.META.get('HTTP_REFERER', '')[:500],
            )
            
            # Adiciona dados de geolocalização
            if geo_data:
                access_log.country = geo_data.get('country_name', 'Brasil')
                access_log.country_code = geo_data.get('country_code', 'BR')
                access_log.state = self.normalize_state_name(geo_data.get('region', ''))
                access_log.state_code = geo_data.get('region_code', '')
                access_log.city = geo_data.get('city', '')
                access_log.postal_code = geo_data.get('postal', '')
                access_log.latitude = geo_data.get('latitude')
                access_log.longitude = geo_data.get('longitude')
                access_log.isp = geo_data.get('org', '')
            
            # Adiciona usuário se estiver autenticado
            if request.user.is_authenticated:
                access_log.user = request.user
            
            # Salva no banco de dados de forma assíncrona se possível
            access_log.save()
            
            # Adiciona o log ao request para uso posterior
            request.access_log = access_log
            
        except Exception as e:
            logger.error(f"Erro ao processar geolocalização: {str(e)}")
        
        return None
    
    def get_client_ip(self, request):
        """
        Obtém o IP real do cliente, considerando proxies
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_geolocation(self, ip_address):
        """
        Busca dados de geolocalização usando a API ipapi.co (gratuita)
        """
        try:
            # API gratuita com limite de 1000 requisições/dia
            response = requests.get(
                f'https://ipapi.co/{ip_address}/json/',
                timeout=5,
                headers={'User-Agent': 'MotorCalcPro/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Se a API retornar erro, tenta API alternativa
                if data.get('error'):
                    return self.get_geolocation_fallback(ip_address)
                
                return data
            else:
                return self.get_geolocation_fallback(ip_address)
                
        except Exception as e:
            logger.error(f"Erro ao buscar geolocalização para IP {ip_address}: {str(e)}")
            return self.get_geolocation_fallback(ip_address)
    
    def get_geolocation_fallback(self, ip_address):
        """
        API de fallback para geolocalização (ip-api.com - também gratuita)
        """
        try:
            response = requests.get(
                f'http://ip-api.com/json/{ip_address}',
                timeout=5,
                params={
                    'fields': 'status,country,countryCode,region,regionName,city,zip,lat,lon,isp,org'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    # Converte para formato compatível
                    return {
                        'country_name': data.get('country', 'Brasil'),
                        'country_code': data.get('countryCode', 'BR'),
                        'region': data.get('regionName', ''),
                        'region_code': data.get('region', ''),
                        'city': data.get('city', ''),
                        'postal': data.get('zip', ''),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'org': data.get('org', ''),
                        'isp': data.get('isp', '')
                    }
        except Exception as e:
            logger.error(f"Erro na API de fallback: {str(e)}")
        
        return {}
    
    def normalize_state_name(self, state_name):
        """
        Normaliza nomes de estados brasileiros
        """
        state_mapping = {
            'sao paulo': 'São Paulo',
            'sp': 'São Paulo',
            'rio de janeiro': 'Rio de Janeiro',
            'rj': 'Rio de Janeiro',
            'minas gerais': 'Minas Gerais',
            'mg': 'Minas Gerais',
            'rio grande do sul': 'Rio Grande do Sul',
            'rs': 'Rio Grande do Sul',
            'parana': 'Paraná',
            'pr': 'Paraná',
            'santa catarina': 'Santa Catarina',
            'sc': 'Santa Catarina',
            'bahia': 'Bahia',
            'ba': 'Bahia',
            'pernambuco': 'Pernambuco',
            'pe': 'Pernambuco',
            'ceara': 'Ceará',
            'ce': 'Ceará',
            'goias': 'Goiás',
            'go': 'Goiás',
            'distrito federal': 'Distrito Federal',
            'df': 'Distrito Federal',
            'espirito santo': 'Espírito Santo',
            'es': 'Espírito Santo',
            'maranhao': 'Maranhão',
            'ma': 'Maranhão',
            'mato grosso': 'Mato Grosso',
            'mt': 'Mato Grosso',
            'mato grosso do sul': 'Mato Grosso do Sul',
            'ms': 'Mato Grosso do Sul',
            'para': 'Pará',
            'pa': 'Pará',
            'paraiba': 'Paraíba',
            'pb': 'Paraíba',
            'piaui': 'Piauí',
            'pi': 'Piauí',
            'rio grande do norte': 'Rio Grande do Norte',
            'rn': 'Rio Grande do Norte',
            'sergipe': 'Sergipe',
            'se': 'Sergipe',
            'alagoas': 'Alagoas',
            'al': 'Alagoas',
            'tocantins': 'Tocantins',
            'to': 'Tocantins',
            'rondonia': 'Rondônia',
            'ro': 'Rondônia',
            'acre': 'Acre',
            'ac': 'Acre',
            'amazonas': 'Amazonas',
            'am': 'Amazonas',
            'roraima': 'Roraima',
            'rr': 'Roraima',
            'amapa': 'Amapá',
            'ap': 'Amapá',
        }
        
        # Normaliza a string
        normalized = state_name.lower().strip()
        return state_mapping.get(normalized, state_name)


class CalculationTrackingMiddleware(MiddlewareMixin):
    """
    Middleware adicional para rastrear especificamente os cálculos realizados
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Intercepta views específicas de cálculo para registrar
        """
        if request.method == 'POST':
            # Mapeia URLs para tipos de cálculo
            calculation_mapping = {
                '/calculo/': 'potencia',
                '/espiras/': 'espiras',
                '/diagrama/': 'diagrama',
            }
            
            calc_type = calculation_mapping.get(request.path)
            
            if calc_type and hasattr(request, 'access_log'):
                # Atualiza o log existente
                request.access_log.access_type = 'calculation'
                request.access_log.calculation_type = calc_type
                request.access_log.save(update_fields=['access_type', 'calculation_type'])
        
        return None