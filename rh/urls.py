from django.urls import path
from . import views

app_name = 'rh'

urlpatterns = [
    path('', views.index, name='index'),
    path('empregados/', views.empregados, name='empregados'),
    path('empregados/cadastrar/', views.empregados_cadastrar, name='empregados_cadastrar'),
]