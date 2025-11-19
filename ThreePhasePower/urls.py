from django.urls import path
from .views import calculo

urlpatterns = [
    path('calculo/', calculo, name='calculo'),
]