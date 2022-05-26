from django.contrib import admin
from nested_inline.admin import NestedTabularInline, NestedModelAdmin
from .models import (Categorias,Cliente,
Promocao,PromocaoCondicao,PromocaoProduto,Produto,ProdutoPreco,
ProdutoBarra,ProdutoPeriodo,Periodo,Pedido,PedidoItem,PedidoPeriodo,Banner,Lista,ListaProduto)
# Register your models here.

class ListaProdutoTabularInline(admin.TabularInline):
    model = ListaProduto
    extra = 0


class ListaAdmin(admin.ModelAdmin):
    inlines = [ListaProdutoTabularInline]
    class Meta:
        model = Lista


class PromocaoCondicaoTabularInline(admin.TabularInline):
    model = PromocaoCondicao
    extra = 0

class PromocaoProdutoTabularInline(admin.TabularInline):
    model = PromocaoProduto
    extra = 0


class PromocaoAdmin(admin.ModelAdmin):

    inlines = [PromocaoCondicaoTabularInline,PromocaoProdutoTabularInline]

    list_display = ('descricao','tipo_condicao','tipo_desconto')

    search_fields = ('descricao',)
    ordering = ('descricao',)
    filter_horizontal = ()

class ClienteAdmin(admin.ModelAdmin):

    list_display = ('representante','id','cnpj', 'nome','valor_aberto', 'tabela_precos','comissao')

    search_fields = ('nome',)
    ordering = ('nome',)
    filter_horizontal = ()



class ProdutoBarraTabularInline(admin.TabularInline):
    model = ProdutoBarra
    readonly_fields = ('barra',)
    can_delete = False
    extra = 0

class ProdutoPrecoTabularInline(admin.TabularInline):
    model = ProdutoPreco
    readonly_fields = ('tabela','preco')
    can_delete = False
    extra = 0

class ProdutoPeriodoTabularInline(admin.TabularInline):
    model = ProdutoPeriodo
    readonly_fields = ('produto','periodo','dados','qtd_total')
    
    can_delete = False
    extra = 0


class ProdutoAdmin(admin.ModelAdmin):

    inlines = [ProdutoPrecoTabularInline,ProdutoBarraTabularInline,ProdutoPeriodoTabularInline]
    list_display = ('produto','desconto','colecao','categoria','subcategoria','atualizacao')
    list_editable = ['desconto',]
    readonly_fields=('produto','descricao','sortido','composicao','linha','categoria','subcategoria','qtd_tamanhos',
    'tamanhos','periodos','precos','qtd_total',
    'colecao','categoria','subcategoria','atualizacao','url_imagem',)

    search_fields = ('produto',)
    ordering = ('produto',)
    filter_horizontal = ()

# class ProdutoPeriodoAdmin(admin.ModelAdmin):

#     list_display = ('produto','periodo')

#     search_fields = ('produto__produto',)
#     ordering = ('produto__produto',)
#     filter_horizontal = ()






class PedidoItemInline(NestedTabularInline):
    model = PedidoItem
    extra = 0
    fk_name = 'pedido_periodo'

    readonly_fields=('produto','pedido_periodo','qtds','desconto','preco','qtd_item','qtd_item_entregar','valor_item','valor_item_entregar','periodos_alteracao','observacao_item')

class PedidoPeriodoInline(NestedTabularInline):
    model = PedidoPeriodo
    extra = 0
    fk_name = 'pedido'
    inlines = [PedidoItemInline]

    readonly_fields=('periodo','qtd_periodo','qtd_periodo_entregar','valor_periodo','valor_periodo_entregar')

class PedidoAdmin(NestedModelAdmin):

    inlines = [PedidoPeriodoInline]

    list_display = (
    'user','cliente','codigo_erp','tipo_venda','liberado_rep','is_teste',
    'colecao','qtd_total','valor_total','data_criacao','ultima_atualiz')

    readonly_fields=('data_criacao','data_liberacao','ultima_atualiz','codigo_erp','valor_total','qtd_total','valor_total_entregar','qtd_total_entregar',
    'dados')

    search_fields = ('cliente__nome','user__name',)
    ordering = ('id',)
    filter_horizontal = ()



# class PedidoPeriodoAdmin(admin.ModelAdmin):

#     list_display = ('pedido','periodo','qtd_periodo','valor_periodo')

#     search_fields = ('pedido__cliente__nome',)
#     ordering = ('id',)
#     filter_horizontal = ()

# class PedidoItemAdmin(admin.ModelAdmin):

#     list_display = ('pedido_periodo','produto','desconto','preco','qtd_item','valor_item')

#     search_fields = ('produto__produto','pedido_periodo__pedido__cliente__nome')
#     ordering = ('id',)
#     filter_horizontal = ()



admin.site.register(Pedido,PedidoAdmin)
# admin.site.register(PedidoPeriodo,PedidoPeriodoAdmin)
# admin.site.register(PedidoItem,PedidoItemAdmin)
# admin.site.register(ProdutoPeriodo,ProdutoPeriodoAdmin)
admin.site.register(Periodo)
admin.site.register(Produto,ProdutoAdmin)
admin.site.register(Promocao,PromocaoAdmin)
admin.site.register(Categorias)
admin.site.register(Banner)
admin.site.register(Cliente,ClienteAdmin)
admin.site.register(Lista,ListaAdmin)
# admin.site.register(DescontoProduto,DescontoProdutoAdmin)