from django import forms
from .models import Colaborador

class ColaboradorForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = [
            'nome_completo', 'data_nascimento', 'cpf', 'rg', 'estado_civil', 'genero', 'nacionalidade',
            'naturalidade', 'email', 'telefone', 'celular', 'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'estado', 'data_admissao_primeiro_vinculo', 'status'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'data_admissao_primeiro_vinculo': forms.DateInput(attrs={'type': 'date'}),
            'estado': forms.Select(choices=[
                ('SP', 'São Paulo'),
                ('AC', 'Acre'),
                ('AL', 'Alagoas'),
                ('AP', 'Amapá'),
                ('AM', 'Amazonas'),
                ('BA', 'Bahia'),
                ('CE', 'Ceará'),
                ('DF', 'Distrito Federal'),
                ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'),
                ('MA', 'Maranhão'),
                ('MT', 'Mato Grosso'),
                ('MS', 'Mato Grosso do Sul'),
                ('MG', 'Minas Gerais'),
                ('PA', 'Pará'),
                ('PB', 'Paraíba'),
                ('PR', 'Paraná'),
                ('PE', 'Pernambuco'),
                ('PI', 'Piauí'),
                ('RJ', 'Rio de Janeiro'),
                ('RN', 'Rio Grande do Norte'),
                ('RS', 'Rio Grande do Sul'),
                ('RO', 'Rondônia'),
                ('RR', 'Roraima'),
                ('SC', 'Santa Catarina'),
                ('SE', 'Sergipe'),
                ('TO', 'Tocantins'),
            ]),
            'genero': forms.Select(choices=[('masculino', 'Masculino'), ('feminino', 'Feminino')]),
        }

