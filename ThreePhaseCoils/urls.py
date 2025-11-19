from django.urls import path
from . import views

urlpatterns = [
    # Página principal
    path('espiras/', views.calculo_espiras, name='espiras'),
    
    # APIs AJAX para carregar opções dinamicamente
    path('api/polos/', views.api_get_polos, name='api_get_polos'),
    path('api/camadas/', views.api_get_camadas, name='api_get_camadas'),
    path('api/g-types/', views.api_get_g_types, name='api_get_g_types'),
    path('api/passos/', views.api_get_passos, name='api_get_passos'),
    path('api/configuracao/', views.api_get_info_configuracao, name='api_get_info_configuracao'),
]