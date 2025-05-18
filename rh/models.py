from django.db import models
from django.conf import settings # Importar settings para referenciar o modelo User
from django.core.validators import FileExtensionValidator

# Função para definir o caminho de upload dos documentos
def user_directory_path(instance, filename):
    # O arquivo será upado para MEDIA_ROOT/user_<id>/<filename>
    return f'documentos/colaborador_{instance.colaborador.id}/{filename}'

class Colaborador(models.Model):
    """
    Cadastro unificado de dados pessoais e profissionais do colaborador.
    """
    # Dados Pessoais
    nome_completo = models.CharField(max_length=255)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=11, unique=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    estado_civil = models.CharField(max_length=50, blank=True, null=True)
    genero = models.CharField(max_length=20, blank=True, null=True)
    nacionalidade = models.CharField(max_length=100, default='Brasileira')
    naturalidade = models.CharField(max_length=100, blank=True, null=True)

    # Contato
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)

    # Endereço
    cep = models.CharField(max_length=8, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)

    # Dados Profissionais Iniciais (pode ser mais detalhado no VinculoEmpregaticio)
    data_admissao_primeiro_vinculo = models.DateField(blank=True, null=True) # Data da primeira admissão na empresa
    status = models.CharField(
        max_length=20,
        choices=[('ativo', 'Ativo'), ('inativo', 'Inativo'), ('afastado', 'Afastado')],
        default='ativo'
    )

    # Pode ser útil linkar a um usuário do sistema, se o colaborador tiver acesso
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='colaborador_perfil')

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_completo

class VinculoEmpregaticio(models.Model):
    """
    Histórico completo de vínculos empregatícios do colaborador na empresa.
    Permite gerenciar diferentes contratos ou mudanças de cargo/salário.
    """
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='vinculos')
    tipo_contrato = models.CharField(
        max_length=50,
        choices=[('clt', 'CLT'), ('pj', 'PJ'), ('estagio', 'Estágio'), ('outro', 'Outro')]
    )
    cargo = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True) # Para vínculos encerrados
    salario_base = models.DecimalField(max_digits=10, decimal_places=2)
    carga_horaria_semanal = models.IntegerField(blank=True, null=True)
    matricula = models.CharField(max_length=50, unique=True, blank=True, null=True) # Matrícula interna, se houver

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.colaborador.nome_completo} - {self.cargo} ({self.data_inicio} to {self.data_fim if self.data_fim else "Present"})'

class DocumentoDigitalizado(models.Model):
    """
    Armazena documentos digitalizados relacionados a um colaborador ou vínculo.
    """
    colaborador = models.ForeignKey(Colaborador, on_delete=models.CASCADE, related_name='documentos')
    vinculo = models.ForeignKey(VinculoEmpregaticio, on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos') # Opcional, pode ser um doc geral do colaborador
    tipo_documento = models.CharField(
        max_length=100,
        choices=[
            ('ctps', 'CTPS'),
            ('rg', 'RG'),
            ('cpf', 'CPF'),
            ('comprovante_residencia', 'Comprovante de Residência'),
            ('certificado_escolaridade', 'Certificado de Escolaridade'),
            ('exame_admissional', 'Exame Admissional'),
            ('contrato_trabalho', 'Contrato de Trabalho'),
            ('ficha_registro', 'Ficha de Registro'),
            ('outro', 'Outro')
        ]
    )
    arquivo = models.FileField(
        upload_to=user_directory_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    descricao = models.TextField(blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tipo_documento} - {self.colaborador.nome_completo}'

class PrazoTrabalhista(models.Model):
    """
    Acompanhamento de prazos importantes (experiência, aviso prévio, etc.).
    """
    vinculo = models.ForeignKey(VinculoEmpregaticio, on_delete=models.CASCADE, related_name='prazos')
    tipo_prazo = models.CharField(
        max_length=50,
        choices=[
            ('experiencia_45', 'Término Contrato Experiência 45 dias'),
            ('experiencia_90', 'Término Contrato Experiência 90 dias'),
            ('aviso_previo', 'Término Aviso Prévio'),
            ('desligamento', 'Data de Desligamento'),
            ('outro', 'Outro')
        ]
    )
    data_prazo = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    cumprido = models.BooleanField(default=False)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tipo_prazo} for {self.vinculo.colaborador.nome_completo} on {self.data_prazo}'

class ObrigacaoLegal(models.Model):
    """
    Gerenciamento e registro de obrigações legais (FGTS, INSS, etc.) por período.
    """
    vinculo = models.ForeignKey(VinculoEmpregaticio, on_delete=models.CASCADE, related_name='obrigacoes_legais')
    tipo_obrigacao = models.CharField(
        max_length=50,
        choices=[
            ('fgts', 'FGTS'),
            ('inss', 'INSS'),
            ('irrf', 'IRRF'),
            ('rais', 'RAIS'),
            ('e_social', 'eSocial'),
            ('outro', 'Outro')
        ]
    )
    periodo_referencia = models.DateField() # Ex: Primeiro dia do mês de referência
    data_vencimento = models.DateField(blank=True, null=True)
    data_pagamento = models.DateField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cumprida = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tipo_obrigacao} for {self.vinculo.colaborador.nome_completo} ({self.periodo_referencia.strftime("%Y-%m")})'

class HistoricoPagamento(models.Model):
    """
    Registro de cada folha de pagamento gerada para um colaborador em um determinado período.
    """
    vinculo = models.ForeignKey(VinculoEmpregaticio, on_delete=models.CASCADE, related_name='historico_pagamentos')
    periodo_referencia = models.DateField() # Ex: Primeiro dia do mês de referência
    data_pagamento = models.DateField()
    salario_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    total_descontos = models.DecimalField(max_digits=10, decimal_places=2)
    salario_liquido = models.DecimalField(max_digits=10, decimal_places=2)
    observacoes = models.TextField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pagamento {self.periodo_referencia.strftime("%Y-%m")} - {self.vinculo.colaborador.nome_completo}'

class ItemFolhaPagamento(models.Model):
    """
    Detalhes dos proventos e descontos dentro de uma folha de pagamento específica.
    """
    historico_pagamento = models.ForeignKey(HistoricoPagamento, on_delete=models.CASCADE, related_name='itens')
    tipo_item = models.CharField(
        max_length=20,
        choices=[('provento', 'Provento'), ('desconto', 'Desconto')]
    )
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.descricao}: {self.valor} ({self.tipo_item})'

class BancoDeHoras(models.Model):
    """
    Controle preciso de banco de horas (créditos/débitos).
    Cada registro representa um lançamento no banco de horas.
    """
    vinculo = models.ForeignKey(VinculoEmpregaticio, on_delete=models.CASCADE, related_name='banco_horas')
    data = models.DateField()
    tipo_lancamento = models.CharField(
        max_length=10,
        choices=[('credito', 'Crédito'), ('debito', 'Débito')]
    )
    horas = models.DecimalField(max_digits=5, decimal_places=2) # Ex: 2.50 para 2 horas e 30 minutos
    justificativa = models.TextField(blank=True, null=True)
    aprovado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True) # Usuário que aprovou
    data_aprovacao = models.DateTimeField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tipo_lancamento} de {self.horas}h em {self.data} for {self.vinculo.colaborador.nome_completo}'

    # Opcional: Propriedade para calcular o saldo atual do banco de horas para um vínculo
    # def get_saldo(self):
    #     creditos = self.vinculo.banco_horas.filter(tipo_lancamento='credito').aggregate(models.Sum('horas'))['horas__sum'] or 0
    #     debitos = self.vinculo.banco_horas.filter(tipo_lancamento='debito').aggregate(models.Sum('horas'))['horas__sum'] or 0
    #     return creditos - debitos


class ProgramacaoFerias(models.Model):
    """
    Registro e programação de férias.
    """
    vinculo = models.ForeignKey(VinculoEmpregaticio, on_delete=models.CASCADE, related_name='programacao_ferias')
    periodo_aquisitivo_inicio = models.DateField()
    periodo_aquisitivo_fim = models.DateField()
    data_inicio_gozo = models.DateField()
    data_fim_gozo = models.DateField()
    dias_gozados = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=[('programada', 'Programada'), ('em_andamento', 'Em Andamento'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada')],
        default='programada'
    )
    observacoes = models.TextField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Férias de {self.vinculo.colaborador.nome_completo} ({self.data_inicio_gozo} to {self.data_fim_gozo})'

class AtestadoMedico(models.Model):
    """
    Registro de atestados médicos apresentados pelos colaboradores.
    """
    vinculo = models.ForeignKey(VinculoEmpregaticio, on_delete=models.CASCADE, related_name='atestados_medicos')
    data_emissao = models.DateField()
    data_inicio_afastamento = models.DateField()
    data_fim_afastamento = models.DateField()
    cid = models.CharField(max_length=10, blank=True, null=True)
    medico_nome = models.CharField(max_length=100, blank=True, null=True)
    medico_crm = models.CharField(max_length=20, blank=True, null=True)
    documento_atestado = models.FileField(
        upload_to=user_directory_path, # Reutiliza a função de upload
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True
    )
    observacoes = models.TextField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Atestado Médico for {self.vinculo.colaborador.nome_completo} ({self.data_inicio_afastamento} to {self.data_fim_afastamento})'