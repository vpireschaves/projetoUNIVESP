from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings # Para linkar com o modelo User, se necessário

try:
    from rh.models import HistoricoPagamento
    from veiculos.models import Abastecimento, Manutencao
except ImportError:
    HistoricoPagamento = None
    Abastecimento = None
    Manutencao = None

class ContaContabil(models.Model):
    """
    Plano de contas da empresa (Receitas, Despesas, Ativos, Passivos, Patrimônio Líquido).
    Permite hierarquias se necessário (conta pai).
    """
    nome = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('receita', 'Receita'),
            ('despesa', 'Despesa'),
            ('ativo', 'Ativo'),
            ('passivo', 'Passivo'),
            ('patrimonio_liquido', 'Patrimônio Líquido')
        ]
    )
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True) # Código contábil
    conta_pai = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcontas')
    aceita_lancamentos = models.BooleanField(default=True) # Indica se lançamentos podem ser feitos diretamente nesta conta

    def __str__(self):
        return self.nome

class CentroCusto(models.Model):
    """
    Classificação das despesas/receitas por área, projeto ou departamento.
    """
    nome = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Pessoa(models.Model):
    """
    Base para Clientes e Fornecedores (individuais ou jurídicos).
    """
    TIPO_CHOICES = [
        ('fisica', 'Pessoa Física'),
        ('juridica', 'Pessoa Jurídica'),
    ]
    nome_razao_social = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cpf_cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True) # CPF ou CNPJ
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cep = models.CharField(max_length=8, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_razao_social

class Cliente(models.Model):
    """
    Detalhes específicos para Clientes.
    """
    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, primary_key=True, related_name='cliente_info')
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.pessoa.nome_razao_social

class Fornecedor(models.Model):
    """
    Detalhes específicos para Fornecedores.
    """
    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, primary_key=True, related_name='fornecedor_info')
    prazo_pagamento_padrao = models.IntegerField(blank=True, null=True) # Dias para pagamento padrão

    def __str__(self):
        return self.pessoa.nome_razao_social

class ContaBancaria(models.Model):
    """
    Dados das contas bancárias da empresa.
    """
    banco = models.CharField(max_length=100)
    agencia = models.CharField(max_length=20)
    numero_conta = models.CharField(max_length=50, unique=True)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Pode ser calculado
    ativa = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.banco} - Ag: {self.agencia} - Cc: {self.numero_conta}'

class ContaCartao(models.Model):
    """
    Dados das contas de cartão (crédito/débito) da empresa.
    """
    bandeira = models.CharField(max_length=50)
    numero_final = models.CharField(max_length=4) # Apenas os últimos 4 dígitos por segurança
    tipo = models.CharField(max_length=10, choices=[('credito', 'Crédito'), ('debito', 'Débito')])
    titular = models.CharField(max_length=100, blank=True, null=True)
    ativa = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.bandeira} ({self.tipo}) - Final: {self.numero_final}'

class NotaFiscal(models.Model):
    """
    Registro das notas fiscais emitidas (saída) ou recebidas (entrada).
    """
    TIPO_CHOICES = [('entrada', 'Entrada'), ('saida', 'Saída')]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    numero = models.CharField(max_length=50)
    serie = models.CharField(max_length=20, blank=True, null=True)
    data_emissao = models.DateField()
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='notas_fiscais_saida')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='notas_fiscais_entrada')
    arquivo_xml = models.FileField(upload_to='notas_fiscais/xml/', blank=True, null=True) # Opcional: Armazenar XML
    arquivo_pdf_danfe = models.FileField(upload_to='notas_fiscais/danfe/', blank=True, null=True) # Opcional: Armazenar PDF
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('tipo', 'numero', 'serie', 'fornecedor', 'cliente') # Garante unicidade da NF

    def __str__(self):
        return f'NF {self.tipo.capitalize()} {self.numero}{"-"+self.serie if self.serie else ""} - {self.data_emissao}'

class LancamentoFinanceiro(models.Model):
    """
    Registro de cada movimentação financeira (entrada ou saída).
    Base para o Fluxo de Caixa.
    """
    TIPO_LANCAMENTO_CHOICES = [('receita', 'Receita'), ('despesa', 'Despesa')]
    STATUS_CHOICES = [('aberto', 'Aberto'), ('quitado', 'Quitado'), ('cancelado', 'Cancelado')]

    tipo_lancamento = models.CharField(max_length=10, choices=TIPO_LANCAMENTO_CHOICES)
    data_vencimento = models.DateField() # Data prevista para receber/pagar
    data_competencia = models.DateField(blank=True, null=True) # Mês/ano a que se refere o lançamento
    data_pagamento_recebimento = models.DateField(blank=True, null=True) # Data real de quitação
    valor_original = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    valor_quitado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='aberto')
    descricao = models.TextField()

    conta_contabil = models.ForeignKey(ContaContabil, on_delete=models.PROTECT, related_name='lancamentos') # Não deletar conta contábil com lançamentos
    centro_custo = models.ForeignKey(CentroCusto, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamentos')

    # Links para Cliente/Fornecedor (usar Pessoa para generalizar)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamentos_financeiros')

    # Links para Contas Bancárias/Cartões (onde o dinheiro entrou/saiu)
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamentos')
    conta_cartao = models.ForeignKey(ContaCartao, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamentos')

    # Link para Nota Fiscal (opcional, um lançamento pode estar associado a uma NF)
    nota_fiscal = models.ForeignKey(NotaFiscal, on_delete=models.SET_NULL, null=True, blank=True, related_name='lancamentos')

    # Links para integração com outros módulos (usando ForeignKey para simplicidade)
    # Certifique-se que os nomes dos apps e modelos estão corretos e que eles existem
    historico_pagamento = models.ForeignKey(
        'rh.HistoricoPagamento', # Use 'rh' ou o nome correto do seu app RH
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lancamentos_financeiros'
    )
    abastecimento = models.ForeignKey(
        'veiculos.Abastecimento', # Use 'veiculos' ou o nome correto do seu app Veiculos
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lancamentos_financeiros'
    )
    manutencao = models.ForeignKey(
        'veiculos.Manutencao', # Use 'veiculos' ou o nome correto do seu app Veiculos
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lancamentos_financeiros'
    )
    # Adicione mais FKs para outras possíveis integrações (ex: compra de insumos, etc.)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.tipo_lancamento.capitalize()} - {self.descricao} ({self.data_vencimento})'

    # Opcional: Métodos para calcular saldo, juros, multas, etc.