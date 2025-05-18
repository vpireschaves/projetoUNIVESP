from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Colaborador
from .forms import ColaboradorForm

def index(request):
    """
    View para a página inicial do módulo Controle de RH.
    """
    # Renderiza o template rh/index.html
    return render(request, 'rh/index.html')

def empregados(request):
    """
    View para a página de empregados do módulo Controle de RH.
    """
    # Renderiza o template rh/empregados.html

    # Pega todos os empregados do banco
    empregados = Colaborador.objects.all()
    
    # Passa a lista de empregados para o template
    context = {
        'empregados': empregados
    }
    return render(request, 'rh/empregados.html', context)

def empregados_cadastrar(request):
    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colaborador cadastrado com sucesso!')
            return redirect('/rh/empregados')
        else:
            messages.error(request, 'Erro ao cadastrar colaborador!')
    else:
        form = ColaboradorForm()
    return render(request, 'rh/empregados_cadastrar.html', {'form': form})