from django.shortcuts import render

def index(request):
    """
    View para a página inicial do módulo Veículos.
    """
    # Renderiza o template veiculos/index.html
    return render(request, 'veiculos/index.html')