from django.shortcuts import render


def diagrama(request):
    """View para a página inicial"""
    return render(request, 'diagrama.html')