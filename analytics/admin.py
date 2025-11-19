# analytics/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import AccessLog, DailyStatsSummary, GeographicRegion
import json


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    """
    Interface administrativa para visualizar logs de acesso
    """
    list_display = [
        'timestamp', 'location_display', 'ip_address', 
        'access_type', 'calculation_type', 'path', 'is_mobile'
    ]
    list_filter = [
        'access_type', 'calculation_type', 'is_mobile', 'is_bot',
        'state', 'city', 'timestamp'
    ]
    search_fields = ['ip_address', 'city', 'state', 'path']
    readonly_fields = [
        'timestamp', 'ip_address', 'user_agent', 'path',
        'country', 'state', 'city', 'latitude', 'longitude',
        'isp', 'organization', 'is_mobile', 'is_bot'
    ]
    date_hierarchy = 'timestamp'
    
    def changelist_view(self, request, extra_context=None):
        """
        Adiciona estatísticas resumidas ao topo da lista
        """
        extra_context = extra_context or {}
        
        # Estatísticas do dia
        today = timezone.now().date()
        today_stats = AccessLog.objects.filter(date=today)
        
        extra_context['today_visits'] = today_stats.count()
        extra_context['today_calculations'] = today_stats.filter(
            access_type='calculation'
        ).count()
        extra_context['today_unique_ips'] = today_stats.values('ip_address').distinct().count()
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(DailyStatsSummary)
class DailyStatsSummaryAdmin(admin.ModelAdmin):
    """
    Interface para visualizar resumos diários
    """
    list_display = [
        'date', 'total_visits', 'unique_visitors', 
        'total_calculations', 'mobile_visits', 'desktop_visits'
    ]
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = [
        'date', 'total_visits', 'unique_visitors', 'total_calculations',
        'potencia_calculations', 'espiras_calculations', 'diagrama_calculations',
        'mobile_visits', 'desktop_visits', 'top_states', 'top_cities'
    ]


@admin.register(GeographicRegion)
class GeographicRegionAdmin(admin.ModelAdmin):
    """
    Interface para gerenciar regiões geográficas
    """
    list_display = ['state_name', 'state_code', 'region']
    list_filter = ['region']
    search_fields = ['state_name', 'state_code']


class AnalyticsAdminSite(admin.AdminSite):
    """
    Site administrativo customizado com dashboard de analytics
    """
    site_header = 'MotorCalcPro - Analytics'
    site_title = 'Analytics Dashboard'
    index_title = 'Dashboard de Análise Geográfica'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/dashboard/', self.admin_view(self.analytics_dashboard_view), 
                 name='analytics_dashboard'),
            path('analytics/heatmap/', self.admin_view(self.heatmap_view), 
                 name='analytics_heatmap'),
            path('analytics/api/map-data/', self.admin_view(self.map_data_api), 
                 name='analytics_map_data'),
        ]
        return custom_urls + urls
    
    def analytics_dashboard_view(self, request):
        """
        View principal do dashboard de analytics
        """
        # Filtros de período
        period = request.GET.get('period', '7days')
        
        # Calcula data inicial baseada no período
        end_date = timezone.now()
        if period == '7days':
            start_date = end_date - timedelta(days=7)
        elif period == '30days':
            start_date = end_date - timedelta(days=30)
        elif period == '1year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Busca dados do período
        access_logs = AccessLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).exclude(is_bot=True)
        
        # Estatísticas gerais
        total_visits = access_logs.count()
        unique_visitors = access_logs.values('ip_address').distinct().count()
        total_calculations = access_logs.filter(access_type='calculation').count()
        
        # Top estados
        top_states = access_logs.exclude(state='').values('state').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Top cidades
        top_cities = access_logs.exclude(city='').values('city', 'state').annotate(
            count=Count('id')
        ).order_by('-count')[:15]
        
        # Cálculos por tipo
        calculations_by_type = {
            'potencia': access_logs.filter(calculation_type='potencia').count(),
            'espiras': access_logs.filter(calculation_type='espiras').count(),
            'diagrama': access_logs.filter(calculation_type='diagrama').count(),
        }
        
        # Acessos por dia (para gráfico)
        daily_visits = []
        current_date = start_date.date()
        while current_date <= end_date.date():
            count = access_logs.filter(date=current_date).count()
            daily_visits.append({
                'date': current_date.strftime('%d/%m'),
                'visits': count
            })
            current_date += timedelta(days=1)
        
        # Dispositivos
        mobile_visits = access_logs.filter(is_mobile=True).count()
        desktop_visits = access_logs.filter(is_mobile=False).count()
        
        context = {
            'title': 'Dashboard de Analytics',
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'total_visits': total_visits,
            'unique_visitors': unique_visitors,
            'total_calculations': total_calculations,
            'top_states': top_states,
            'top_cities': top_cities,
            'calculations_by_type': calculations_by_type,
            'daily_visits': json.dumps(daily_visits),
            'mobile_visits': mobile_visits,
            'desktop_visits': desktop_visits,
            'mobile_percentage': round((mobile_visits / total_visits * 100) if total_visits > 0 else 0, 1),
            'desktop_percentage': round((desktop_visits / total_visits * 100) if total_visits > 0 else 0, 1),
        }
        
        return render(request, 'admin/analytics_dashboard.html', context)
    
    def heatmap_view(self, request):
        """
        View do mapa de calor interativo
        """
        context = {
            'title': 'Mapa de Calor - Acessos por Região',
        }
        return render(request, 'admin/analytics_heatmap.html', context)
    
    def map_data_api(self, request):
        """
        API endpoint para fornecer dados do mapa
        """
        from django.http import JsonResponse
        
        # Filtros
        period = request.GET.get('period', '7days')
        
        # Calcula período
        end_date = timezone.now()
        if period == '7days':
            start_date = end_date - timedelta(days=7)
        elif period == '30days':
            start_date = end_date - timedelta(days=30)
        elif period == '1year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Busca dados agrupados por estado
        state_data = AccessLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date,
            country_code='BR'
        ).exclude(
            Q(state='') | Q(is_bot=True)
        ).values('state', 'state_code').annotate(
            total_visits=Count('id'),
            calculations=Count('id', filter=Q(access_type='calculation'))
        )
        
        # Busca dados agrupados por cidade
        city_data = AccessLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date,
            country_code='BR'
        ).exclude(
            Q(city='') | Q(is_bot=True)
        ).values('city', 'state', 'latitude', 'longitude').annotate(
            total_visits=Count('id'),
            calculations=Count('id', filter=Q(access_type='calculation'))
        ).filter(latitude__isnull=False, longitude__isnull=False)[:100]  # Limita a 100 cidades
        
        # Formata dados para o mapa
        map_data = {
            'states': list(state_data),
            'cities': list(city_data),
            'period': period,
            'start_date': start_date.strftime('%d/%m/%Y'),
            'end_date': end_date.strftime('%d/%m/%Y'),
        }
        
        return JsonResponse(map_data)


# Registra o site customizado
analytics_admin_site = AnalyticsAdminSite(name='analytics_admin')