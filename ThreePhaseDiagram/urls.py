from django.urls import path
from .views import diagrama

urlpatterns = [
    path('diagrama/', diagrama, name='diagrama'), 
]