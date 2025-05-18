from django.shortcuts import render

def index(request):
    """
    View para a página inicial (index).
    """
    # Você pode adicionar lógica aqui no futuro, se necessário.
    # Por enquanto, apenas renderiza o template index.html
    return render(request, 'financeiro/index.html')