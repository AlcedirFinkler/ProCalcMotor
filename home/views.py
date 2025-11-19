from django.shortcuts import render


def index(request):
    """View para a página inicial"""
    return render(request, 'index.html')
