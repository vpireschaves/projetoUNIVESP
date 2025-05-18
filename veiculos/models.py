from django.db import models
from django.core.validators import MinValueValidator

class TipoCombustivel(models.Model):
    """
    Tipos de combustível utilizados pela frota.
    """
    nome = models.CharField(max_length=50, unique=True)
    unidade_medida = models.CharField(
        max_length=10,
        choices=[('diesel', 'Diesel'), ('gasolina', 'Gasolina'), ('etanol', 'Etanol'), ('litro', 'Litro')],
        default='diesel'
    )

    def __str__(self):

        return self.nome

class Veiculo(models.Model):
    """
    Cadastro principal de cada veículo da frota.
    """
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    ano_fabricacao = models.IntegerField()
    chassi = models.CharField(max_length=17, unique=True, blank=True, null=True)
    tipo_veiculo = models.CharField(
        max_length=50,
        choices=[('carro', 'Carro'), ('caminhao', 'Caminhão'), ('trator', 'Trator'), ('moto', 'Moto'), ('outro', 'Outro')],
        default='carro'
    )
    tipo_combustivel = models.ForeignKey(TipoCombustivel, on_delete=models.SET_NULL, null=True, related_name='veiculos')
    capacidade_tanque = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quilometragem_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    ativo = models.BooleanField(default=True)
    data_aquisicao = models.DateField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.marca} {self.modelo} - {self.placa}'

class Abastecimento(models.Model):
    """
    Registro de cada abastecimento realizado.
    Permite monitorar consumo e calcular médias.
    """
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='abastecimentos')
    data_hora = models.DateTimeField()
    tipo_combustivel = models.ForeignKey(TipoCombustivel, on_delete=models.PROTECT) # Proteger a exclusão se houver abastecimentos
    quantidade_litros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    valor_por_litro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quilometragem_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    posto_combustivel = models.CharField(max_length=100, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Abastecimento de {self.quantidade_litros} L em {self.data_hora.strftime("%Y-%m-%d %H:%M")} for {self.veiculo.placa}'

    # Opcional: Adicionar lógica para calcular o custo total ou média de rendimento aqui ou em métodos/managers

class TipoManutencao(models.Model):
    """
    Categorias de manutenção (Preventiva, Corretiva, etc.).
    """
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

class Manutencao(models.Model):
    """
    Registro de cada serviço de manutenção realizado em um veículo.
    Inclui histórico e agendamento de revisões.
    """
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='manutencoes')
    tipo_manutencao = models.ForeignKey(TipoManutencao, on_delete=models.PROTECT) # Proteger a exclusão
    data_servico = models.DateField()
    quilometragem_servico = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    descricao_servico = models.TextField()
    custo_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    oficina = models.CharField(max_length=100, blank=True, null=True)
    proxima_manutencao_data = models.DateField(blank=True, null=True) # Para agendar revisões
    proxima_manutencao_quilometragem = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    observacoes = models.TextField(blank=True, null=True)

    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tipo_manutencao.nome} em {self.data_servico} for {self.veiculo.placa}'

class Implemento(models.Model):
    """
    Cadastro completo de equipamentos agrícolas e outros implementos.
    """
    nome = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, unique=True, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_aquisicao = models.DateField(blank=True, null=True)

    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class VeiculoImplemento(models.Model):
    """
    Modelo intermediário para rastrear o vínculo de implementos com veículos
    e o período em que essa conexão existiu.
    """
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE, related_name='vinculos_implementos')
    implemento = models.ForeignKey(Implemento, on_delete=models.CASCADE, related_name='vinculos_veiculos')
    data_conexao = models.DateField()
    data_desconexao = models.DateField(blank=True, null=True) # Para rastrear o período de uso

    class Meta:
        unique_together = ('veiculo', 'implemento', 'data_conexao') # Garante unicidade para a mesma conexão no mesmo dia

    def __str__(self):
        return f'{self.implemento.nome} conectado a {self.veiculo.placa} from {self.data_conexao} to {self.data_desconexao if self.data_desconexao else "Present"}'