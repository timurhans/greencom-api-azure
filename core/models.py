from django.db import models
from django.contrib.auth.models import User
from account.models import (Account)
from django.utils import timezone


class Categorias(models.Model):
    dados = models.TextField()
    atualizacao = models.DateTimeField(null=True,unique=True)
    def __str__(self):
        return str(self.id)

# credit = models.DecimalField(max_digits=8, decimal_places=2)

class Cliente(models.Model):

    cnpj = models.CharField(max_length=50, null=False, blank=False,unique=True)
    nome = models.CharField(max_length=150, null=False, blank=False,unique=False)
    razao_social = models.CharField(max_length=200,default="sem razao", null=False, blank=False,unique=False)
    valor_aberto = models.DecimalField(max_digits=8, decimal_places=2)
    comissao = models.DecimalField(max_digits=8, decimal_places=2)
    tabela_precos = models.CharField(max_length=4)
    condicao_pagamento = models.CharField(max_length=4)
    desc_cond_pag = models.CharField(max_length=30,default="",null=True,blank=True)
    representante = models.ForeignKey(Account,null=True,blank=True, on_delete=models.CASCADE)
    email = models.EmailField(default="",null=True)
    telefone = models.CharField(default="",max_length=50,null=True)
    whatsapp = models.CharField(default="",max_length=50,null=True)
    uf = models.CharField(default="",max_length=2,null=True)
    cidade = models.CharField(default="",max_length=50,null=True)
    cep = models.CharField(default="",max_length=15,null=True)
    endereco = models.CharField(default="",max_length=150,null=True)
    dados_financeiro = models.TextField(default="",null=True)
    dados_faturamentos = models.TextField(default="",null=True)
    dados_pedidos = models.TextField(default="",null=True)
    visualiza_varejo = models.BooleanField(default=False)
    inativo = models.BooleanField(default=False)


    def __str__(self):
        return str(self.nome)




class Periodo(models.Model):
    periodo_faturamento = models.DateField(null=False, blank=False,unique=True)
    periodo_vendas = models.DateField(null=False, blank=False,)
    desc_periodo = models.CharField(max_length=150,unique=True)
    is_provisorio = models.BooleanField(default=False)
    def __str__(self):
        return str(self.desc_periodo)

class Produto(models.Model):
    produto = models.CharField(max_length=25, null=False, blank=False,unique=True)
    descricao = models.CharField(max_length=100)
    sortido = models.CharField(max_length=50,default="Venda Sortida",null=False, blank=False)
    composicao = models.CharField(default="vazio",max_length=200)
    linha = models.CharField(max_length=50, null=False, blank=False)
    categoria = models.CharField(max_length=50, null=False, blank=False)
    subcategoria = models.CharField(max_length=50, null=False, blank=False)
    url_imagem = models.CharField(max_length=100, null=False, blank=False)
    qtd_tamanhos = models.IntegerField(default=0, null=False, blank=False)
    tamanhos = models.TextField()
    colecao = models.CharField(max_length=50, null=False, blank=False)
    atualizacao = models.DateTimeField(auto_now= True)
    periodos = models.TextField()
    precos = models.TextField()
    qtd_total = models.IntegerField(default=0, null=False, blank=False)
    desconto = models.DecimalField(default=0,max_digits=2, decimal_places=2,null=False,blank=False)
    def __str__(self):
        return str(self.produto)

class ProdutoPreco(models.Model):
    produto = models.ForeignKey(Produto,null=False,blank=False, on_delete=models.CASCADE)
    tabela = models.CharField(max_length=5, null=False, blank=False)
    preco = models.DecimalField(max_digits=8, decimal_places=2,null=False,blank=False)
    def __str__(self):
        return str(self.produto.produto+" - "+self.tabela)

class ProdutoBarra(models.Model):
    produto = models.ForeignKey(Produto,null=False,blank=False, on_delete=models.CASCADE)
    barra = models.CharField(max_length=50, null=False, blank=False,unique=True)
    def __str__(self):
        return str(self.produto.produto+" - "+self.barra)


class ProdutoPeriodo(models.Model):
    produto = models.ForeignKey(Produto,null=False,blank=False, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo,null=False,blank=False, on_delete=models.CASCADE)
    dados = models.TextField()
    qtd_total = models.IntegerField(default=0)
    def __str__(self):
        return str(self.produto.produto+" - "+str(self.periodo.desc_periodo))


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente,null=False,blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(Account,null=False,blank=False, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add= True)
    data_liberacao = models.DateTimeField(default=None,null=True)
    ultima_atualiz = models.DateTimeField(auto_now= True)
    tipo_venda = models.CharField(default='...',max_length=30,null=False, blank=False)
    colecao = models.CharField(default='...',max_length=10, null=False, blank=False)
    codigo_erp = models.CharField(default='...',max_length=10, null=False, blank=False)
    liberado_cliente = models.BooleanField(default=False)
    liberado_rep = models.BooleanField(default=False)
    enviado_fabrica = models.BooleanField(default=False)
    recebido_fabrica = models.BooleanField(default=False)
    is_teste = models.BooleanField(default=False)
    valor_total = models.DecimalField(max_digits=8, decimal_places=2,default=0)
    qtd_total = models.IntegerField(default=0)
    dados = models.TextField(default='',null=True,blank=True)
    observacoes = models.TextField(default='',null=True,blank=True)
    def __str__(self):
        return str(str(self.id)+' - '+str(self.user))

class PedidoPeriodo(models.Model):
    pedido = models.ForeignKey(Pedido,null=False,blank=False, on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo,null=False,blank=False, on_delete=models.CASCADE)
    qtd_periodo = models.IntegerField(default=0)
    valor_periodo = models.DecimalField(max_digits=8, decimal_places=2,default=0)
    def __str__(self):
        return str(self.pedido.cliente)+' - '+self.periodo.desc_periodo

class PedidoItem(models.Model):
    pedido_periodo = models.ForeignKey(PedidoPeriodo,null=False,blank=False, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto,null=False,blank=False, on_delete=models.CASCADE)
    qtds = models.TextField()
    desconto = models.DecimalField(max_digits=8, decimal_places=2,default=0)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    qtd_item = models.IntegerField()
    valor_item = models.DecimalField(max_digits=8, decimal_places=2)
    periodos_alteracao = models.TextField(default="",blank=True,null=True)
    observacao_item = models.CharField(max_length=150,blank=True,null=True,default="")
    def __str__(self):
        return str(self.pedido_periodo.pedido.cliente)+' - '+self.produto.produto

class Promocao(models.Model):
    descricao = models.CharField(max_length=30, null=False, blank=False,unique=True)

    TIPOS_CONDICOES = [
        ('QTD', 'Quantidade'),
        ('VLR', 'Valor'),
    ]
    tipo_condicao = models.CharField(max_length=3,choices=TIPOS_CONDICOES,null=False, blank=False)

    TIPOS_DESCONTO = [
        ('PCT', 'Percentual'),
        ('VLR', 'Valor'),
    ]
    tipo_desconto = models.CharField(max_length=3,choices=TIPOS_DESCONTO,null=False, blank=False)

    def __str__(self):
        return str(self.descricao)

class PromocaoProduto(models.Model):
    promocao = models.ForeignKey(Promocao,null=False,blank=False, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto,null=False,blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return self.promocao.descricao+" - "+self.produto.produto

class PromocaoCondicao(models.Model):
    promocao = models.ForeignKey(Promocao,null=False,blank=False, on_delete=models.CASCADE)
    condicao = models.DecimalField(max_digits=8, decimal_places=2,null=False,blank=False)
    desconto = models.DecimalField(max_digits=8, decimal_places=2,null=False,blank=False)
    def __str__(self):
        return str(self.promocao)


class Banner(models.Model):
    ordem = models.IntegerField()
    link = models.CharField(max_length=1024,null=False, blank=False)
    url_imagem = models.CharField(max_length=1024,null=False, blank=False)
    def __str__(self):
        return str(self.link)


class Lista(models.Model):
    codigo = models.CharField(max_length=30,null=False, blank=False,unique=True)
    ativo = models.BooleanField(default=True)
    def __str__(self):
        return str(self.codigo)
    

class ListaProduto(models.Model):
    lista = models.ForeignKey(Lista,null=False,blank=False, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto,null=False,blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.lista.codigo+" - "+self.produto.produto)

# class DescontoProduto(models.Model):
#     produto = models.ForeignKey(Produto,null=False,blank=False, on_delete=models.CASCADE)
#     desconto = models.DecimalField(max_digits=8, decimal_places=2,null=False,blank=False)
#     def __str__(self):
#         return self.produto.produto+" - "+str(self.desconto)