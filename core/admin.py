from django.contrib import admin
from .models import (Categorias,Cliente,
Promocao,PromocaoCondicao,PromocaoProduto,Produto,ProdutoPreco,
ProdutoBarra,ProdutoPeriodo,Periodo,Pedido,PedidoItem,PedidoPeriodo)
# Register your models here.

class ClienteAdmin(admin.ModelAdmin):

    list_display = ('representante','id','cnpj', 'nome','valor_aberto', 'tabela_precos','comissao')

    search_fields = ('nome',)
    ordering = ('nome',)
    filter_horizontal = ()


class PromocaoAdmin(admin.ModelAdmin):

    list_display = ('descricao','tipo_condicao','tipo_desconto')

    search_fields = ('descricao',)
    ordering = ('descricao',)
    filter_horizontal = ()

class PromocaoCondicaoAdmin(admin.ModelAdmin):

    list_display = ('promocao','condicao','desconto')

    search_fields = ('promocao',)
    ordering = ('promocao',)
    filter_horizontal = ()

class PromocaoProdutoAdmin(admin.ModelAdmin):

    list_display = ('promocao','produto')

    search_fields = ('produto',)
    ordering = ('promocao__descricao',)
    filter_horizontal = ()


class ProdutoAdmin(admin.ModelAdmin):

    list_display = ('produto','descricao','atualizacao','categoria','subcategoria')

    search_fields = ('produto',)
    ordering = ('produto',)
    filter_horizontal = ()

class ProdutoPeriodoAdmin(admin.ModelAdmin):

    list_display = ('produto','periodo')

    search_fields = ('produto__produto',)
    ordering = ('produto__produto',)
    filter_horizontal = ()

class ProdutoBarraAdmin(admin.ModelAdmin):

    list_display = ('produto','barra')

    search_fields = ('produto__produto',)
    ordering = ('produto__produto',)
    filter_horizontal = ()


class ProdutoPrecoAdmin(admin.ModelAdmin):

    list_display = ('produto','preco')

    search_fields = ('produto__produto',)
    ordering = ('produto__produto',)
    filter_horizontal = ()

class PedidoAdmin(admin.ModelAdmin):

    list_display = (
    'user','cliente','codigo_erp','tipo_venda','liberado_rep','is_teste',
    'colecao','qtd_total','valor_total','data_criacao','ultima_atualiz')

    search_fields = ('cliente__nome','user__name',)
    ordering = ('id',)
    filter_horizontal = ()

class PedidoPeriodoAdmin(admin.ModelAdmin):

    list_display = ('pedido','periodo','qtd_periodo','valor_periodo')

    search_fields = ('pedido__cliente__nome',)
    ordering = ('id',)
    filter_horizontal = ()

class PedidoItemAdmin(admin.ModelAdmin):

    list_display = ('pedido_periodo','produto','desconto','preco','qtd_item','valor_item')

    search_fields = ('produto__produto','pedido_periodo__pedido__cliente__nome')
    ordering = ('id',)
    filter_horizontal = ()


admin.site.register(Pedido,PedidoAdmin)
admin.site.register(PedidoPeriodo,PedidoPeriodoAdmin)
admin.site.register(PedidoItem,PedidoItemAdmin)
admin.site.register(ProdutoPreco,ProdutoPrecoAdmin)
admin.site.register(ProdutoBarra,ProdutoBarraAdmin)
admin.site.register(ProdutoPeriodo,ProdutoPeriodoAdmin)
admin.site.register(Periodo)
admin.site.register(Produto,ProdutoAdmin)
admin.site.register(Promocao,PromocaoAdmin)
admin.site.register(PromocaoCondicao,PromocaoCondicaoAdmin)
admin.site.register(PromocaoProduto,PromocaoProdutoAdmin)
admin.site.register(Categorias)
admin.site.register(Cliente,ClienteAdmin)