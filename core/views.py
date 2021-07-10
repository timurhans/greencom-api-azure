#DJANGO IMPORTS
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse,JsonResponse
from django.template.loader import get_template
from django.db.models import Q,Count,Sum,F
from django.utils import timezone
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,AllowAny
from rest_framework.response import Response

import decimal

#APP IMPORTS
from .models import (Produto,ProdutoPreco,ProdutoPeriodo,ProdutoBarra,
        Categorias,Cliente,Periodo,Promocao,PromocaoCondicao,PromocaoProduto,
        Pedido,PedidoPeriodo,PedidoItem)
from params.models import (ColecaoErp,ColecaoB2b,Parametro,Banner)
from account.models import (Account,AccountType)
# THIRD PARTY IMPORTS
from xhtml2pdf import pisa
import json
from datetime import (date,datetime)
import os
import copy


# ----------------------- FUNCOES AUXILIARES --------------------------------

def verifica_query(query):

    if query.isnumeric() and len(query)==13:
        return 'barra'
    elif any(char.isdigit() for char in query) and ' ' not in query:
        return 'produto'
    else:
        #Implementar depois
        return 'descricao'



def define_tipo_venda(colecao):
    
    if colecao == 'VAREJO':
        return 'VAREJO'
    elif colecao == Parametro.objects.get(parametro='COLECAO_VIGENTE').valor:
        return 'COLEÇÃO NORMAL'
    else:
        return 'SALDOS'


def get_produtos(request,tabela_precos,linha,categoria,subcategoria):
    ult_atual = Parametro.objects.get(parametro='ULTIMA_ATUALIZACAO_PRODUTOS')
    ult_atual = datetime.strptime(ult_atual.valor,'%Y-%m-%d')

    sort_params = {}
    sort_params['produto__linha']=linha
    sort_params['produto__categoria']=categoria
    if subcategoria is not None:
        sort_params['produto__subcategoria']=subcategoria
    if 'colecao' in request.GET:
        colecao = request.GET['colecao']
        if colecao is not None:
            if colecao != "Todas":
                cols_erp = list(ColecaoErp.objects.filter(colecaoB2b__active=True,colecaoB2b__title=colecao).values_list('codigo', flat=True).distinct())
                sort_params['produto__colecao__in']=cols_erp
    if 'periodo' in request.GET:
        periodo = request.GET['periodo']
        if periodo is not None:
            if periodo != "Todos":
                periodo = Periodo.objects.get(desc_periodo=periodo)
                sort_params['produto__produtoperiodo__periodo']=periodo

    queryset = ProdutoPreco.objects.select_related('produto').filter(Q(produto__atualizacao__gte=ult_atual),
    tabela=tabela_precos,**sort_params)
    queryset = list(queryset.values('preco','produto__produto','produto__descricao',
    'produto__sortido','produto__composicao','produto__linha','produto__categoria',
    'produto__subcategoria','produto__url_imagem','produto__qtd_tamanhos',
    'produto__tamanhos','produto__colecao','produto__periodos'))
    
    return queryset


def busca_produtos(request,tabela_precos,query):

    ult_atual = Parametro.objects.get(parametro='ULTIMA_ATUALIZACAO_PRODUTOS')
    ult_atual = datetime.strptime(ult_atual.valor,'%Y-%m-%d')

    query = query.upper()

    sort_params = {}
    tipo_query = verifica_query(query)
    if tipo_query=='barra':
        produto = ProdutoBarra.objects.get(barra=query).produto
        sort_params['produto']=produto
    elif tipo_query=='produto':
        produto=query
        sort_params['produto__produto__startswith']=produto
    elif tipo_query=='descricao':
        descricao=query
        sort_params['produto__descricao__contains']=descricao

    if 'colecao' in request.GET:
        colecao = request.GET['colecao']
        if colecao is not None:
            if colecao != "Todas":
                cols_erp = list(ColecaoErp.objects.filter(colecaoB2b__active=True,colecaoB2b__title=colecao).values_list('codigo', flat=True).distinct())
                sort_params['produto__colecao__in']=cols_erp
    

    queryset = ProdutoPreco.objects.select_related('produto').filter(Q(produto__atualizacao__gte=ult_atual),
    tabela=tabela_precos,**sort_params)
    queryset = list(queryset.values('preco','produto__produto','produto__descricao',
    'produto__sortido','produto__composicao','produto__linha','produto__categoria',
    'produto__subcategoria','produto__url_imagem','produto__qtd_tamanhos',
    'produto__tamanhos','produto__colecao','produto__periodos'))
    return queryset 

def verifica_session(request):

    user = request.user

    if user.tipo_conta.is_rep:
        clienteId=None
        clienteNome=None
        isRep=True
    else:
        cliente =  Cliente.objects.get(cnpj=user.login)
        clienteId=cliente.id
        clienteNome=cliente.nome
        isRep=False
    
    return clienteId,clienteNome,isRep


def pedido_pdf(pedido,lista_pedidos):
    # pedido = pedido.__dict__
    # pedido = pedido_to_dict(pedido)
    codigos = [str(ped.id) for ped in lista_pedidos]
    codigos = ','.join(codigos)

    today = date.today().strftime("%d/%m/%Y")
    data = {'pedido' : pedido,
            'data' : today,
            'codigos':codigos
            }

    template = get_template('core/pedido_pdf.html')
    html  = template.render(data)

    file_path = 'static/pdfs/'+str(pedido['id'])+'.pdf'
    file = open(file_path, "w+b")
    pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
            encoding='utf-8')

    file.seek(0)
    pdf = file.read()
    file.close()      
    return file_path

# ----------------------- VIEWS --------------------------------

@api_view(['GET','POST'])
def carrinho(request):

    if request.user.is_authenticated:

        if request.method == 'GET':
            return carrinho_get(request)
        elif request.method == 'POST':
            return carrinho_add(request)
    else:
        return Response({'message': 'Fazer Login','confirmed':False})

# @api_view(['GET','POST'])
def carrinho_add(request,is_update=False):

    #Parametro is_update verifica se origem da adicao vem da vitrine ou do carrinho,
    #  caso seja update do carrinho retorna somente True ou False para que o retorno seja dado na view carrinho_update

    post = request.body
    post = post.decode("utf-8").replace("'", '"')
    post = json.loads(post)
    qtd_item = post['qtd_total']
    valor_item = qtd_item*decimal.Decimal((post['produto']['preco']))

    status,response = carrinho_triagem_processa(post,request.user)

    if status==False:
        return Response(response)
    carrinho = response
              
    try:
        carrinhoPeriodo = PedidoPeriodo.objects.get(pedido=carrinho,periodo__desc_periodo=post['periodo']) 
    except:
        periodo = Periodo.objects.get(desc_periodo=post['periodo'])
        carrinhoPeriodo = PedidoPeriodo(periodo=periodo,pedido=carrinho)
        carrinhoPeriodo.save()
    
    try: 
        PedidoItem.objects.get(pedido_periodo=carrinhoPeriodo,produto__produto=post['produto']['produto__produto'])
        if is_update:
            return False
        else:
            # Fazer logica, para se for caso de is update, alterar quantidades
            return Response({'message':'Produto ja presente no carrinho no periodo','confirmed':False})
    except:
        produto = Produto.objects.get(produto=post['produto']['produto__produto'])
        carrinhoItem = PedidoItem(pedido_periodo=carrinhoPeriodo,preco=post['produto']['preco'],
        qtd_item=qtd_item,valor_item=valor_item,produto=produto,qtds=carrinho_trata_qtds_post(post['qtds']))
        carrinhoItem.save()
        carrinhoPeriodo.qtd_periodo = carrinhoPeriodo.qtd_periodo+qtd_item
        carrinhoPeriodo.valor_periodo = carrinhoPeriodo.valor_periodo+valor_item
        carrinhoPeriodo.save()
    
    carrinho.qtd_total=carrinho.qtd_total+qtd_item
    carrinho.valor_total=carrinho.valor_total+valor_item
    carrinho.save()
    if is_update:
        return True
    else:
        return Response({'message':'Adicionado ao Carrinho com Sucesso','carrinhoId':carrinho.id,'confirmed':True})


def carrinho_trata_qtds_post(qtds):
    # Limpa post de qtds do carrinho, para salvar no BD somente cores que de fato tenham pedido
    keys_delete = []
    for q in qtds:
        qtds_cor = qtds[q]
        flag_zeros = all(v == 0 for v in qtds_cor)
        if flag_zeros:
            keys_delete.append(q)
    for key in keys_delete:
        del qtds[key]
    return json.dumps(qtds)

# @api_view(['GET'])
def carrinho_get(request):

    status,response = carrinho_triagem_processa(request.GET,request.user)

    if status==False:
        return Response(response)
    carrinho = response
    
    dados_carrinho = []
    message = ""
    periodos = PedidoPeriodo.objects.filter(pedido=carrinho).order_by('periodo__periodo_faturamento')
    for per in periodos:
        dados_periodo = {}
        dados_periodo['periodo'] = per.periodo.desc_periodo
        dados_periodo['qtd_periodo'] = per.qtd_periodo
        dados_periodo['valor_periodo'] = per.valor_periodo
        carrinho_item = PedidoItem.objects.filter(pedido_periodo=per)
        dados_periodo['itens'] = list(
            carrinho_item.values('id','produto__produto','produto__descricao','produto__sortido','produto__composicao',
            'produto__categoria','produto__subcategoria','produto__url_imagem','produto__qtd_tamanhos',
            'produto__tamanhos','produto__colecao','produto__periodos','qtds','preco','desconto','qtd_item','valor_item'))
        dados_carrinho.append(dados_periodo)
    if len(dados_carrinho)==0:
        message = "Sem Itens no Carrinho"
    return Response({'dados':dados_carrinho,'valor_total':carrinho.valor_total,
    'qtd_total':carrinho.qtd_total,'carrinhoId':carrinho.id,'is_teste':carrinho.is_teste,
    'observacoes':carrinho.observacoes,'message':message,'confirmed':True})


@api_view(['GET'])
def carrinho_delete_item(request,id):
    #Exclui item do carrinho

    item_carrinho = PedidoItem.objects.get(id=id)

    if (request.user==item_carrinho.pedido_periodo.pedido.user or request.user.login==item_carrinho.pedido_periodo.pedido.cliente.representante.login):
        deleta_item_carrinho(item_carrinho)       
        return Response({'message':'Item excluida com sucesso','carrinhoId':item_carrinho.pedido_periodo.pedido.id,'confirmed':True})
    else:
        return Response({'message':'nao foi possivel excluir','confirmed':False})

@api_view(['GET','POST'])
def carrinho_update(request,id):
    #Atualiza item do carrinho
    item_carrinho = PedidoItem.objects.get(id=id)

    if (request.user==item_carrinho.pedido_periodo.pedido.user or request.user.login==item_carrinho.pedido_periodo.pedido.cliente.representante.login):
        if carrinho_add(request,True):
            item_carrinho = PedidoItem.objects.get(id=id)
            deleta_item_carrinho(item_carrinho)
            return Response({'message':'Alterado com sucesso','carrinhoId':item_carrinho.pedido_periodo.pedido.id,'confirmed':True})
    
    return Response({'message':'nao foi possivel alterar','confirmed':False})

# @api_view(['GET','POST'])                   
def carrinho_triagem(request):
    # Faz a triagem de qual carrinho deve ser utilizado de acordo com os parametros passados na requisicao
    if request.method == "GET":
        return carrinho_triagem_processa(request.GET,request.user)

    else:
        post = request.body
        post = post.decode("utf-8").replace("'", '"')
        post = json.loads(post)
        return carrinho_triagem_processa(post,request.user)


def carrinho_triagem_processa(dadosRequest,user):
    #verifica se request nao tem carrinho id, caso nao tenha = True
    flag_carrinho = True
    if 'carrinhoId' in dadosRequest:
        if dadosRequest['carrinhoId'] is not None:
            flag_carrinho = False
    #verifica se request nao tem cliente id, caso nao tenha = True
    flag_cliente = True
    if 'clienteId' in dadosRequest:
        if dadosRequest['clienteId'] is not None:
            flag_cliente = False
    
    if flag_carrinho:
        if flag_cliente:
            #Caso nao tenha nem carrinho nem cliente, retorna erro
            # return False,Response({'dados':[],'message':'Defina um cliente','confirmed':False})
            return False,{'dados':[],'message':'Defina um cliente','confirmed':False}
        #Caso nao tenha carrinho mas tenha cliente busca ultimo pedido "mexido", caso nao tenha, cria um novo
        cliente = dadosRequest['clienteId']
        if user.tipo_conta.is_rep:
            #Se for rep, busca o ultimo do usuario do rep e cliente selecionado
            ultimos_carrinhos = Pedido.objects.filter(user=user,cliente__id=cliente,liberado_rep=False).order_by('-ultima_atualiz')
            if len(ultimos_carrinhos)>0:
                return True,ultimos_carrinhos[0]              
        else:
            #Se for cliente, busca o ultimo do user do cliente
            ultimos_carrinhos = Pedido.objects.filter(user=user,liberado_rep=False).order_by('-ultima_atualiz')
            if len(ultimos_carrinhos)>0:
                return True,ultimos_carrinhos[0]
                
        cliente =  Cliente.objects.get(id=cliente)
        carrinho = Pedido(cliente=cliente,user=user)
        carrinho.save()
        return True,carrinho  
    else:
        try:
            carrinho = Pedido.objects.get(id=dadosRequest['carrinhoId'],liberado_rep=False)
            return True,carrinho
        except:
            cliente = dadosRequest['clienteId']
            cliente =  Cliente.objects.get(id=cliente)
            carrinho = Pedido(cliente=cliente,user=user)
            carrinho.save()
            return True,carrinho    


def deleta_item_carrinho(item_carrinho):
    qtd_item = item_carrinho.qtd_item
    valor_item = item_carrinho.valor_item
    (qtd,obj) = item_carrinho.delete()
    if qtd==1:
        
        #exclui pedido_periodo se nao tiver mais nenhum item ou diminui qtd e valor caso tenha
        pedido_periodo = item_carrinho.pedido_periodo
        pedido = pedido_periodo.pedido
        itens_periodo = PedidoItem.objects.filter(pedido_periodo=pedido_periodo)
        if len(itens_periodo)==0:
            pedido_periodo.delete()
        else:
            pedido_periodo.qtd_periodo = pedido_periodo.qtd_periodo-qtd_item
            pedido_periodo.valor_periodo = pedido_periodo.valor_periodo-valor_item        
            pedido_periodo.save()
        #Diminui qtd e valor carrinho
        pedido.qtd_total = pedido.qtd_total-qtd_item
        pedido.valor_total = pedido.valor_total-valor_item
        pedido.save()

def pedido_to_dict(ped):

    #Transforma pedido em dicionario serializavel

    ped['cliente'] = Cliente.objects.get(id=ped['cliente_id']).__dict__
    ped['cliente']['valor_aberto'] = str(ped['cliente']['valor_aberto'])
    ped['cliente']['comissao'] = str(ped['cliente']['comissao'])
    del ped['cliente']['_state']
    ped['valor_total'] = str(ped['valor_total'])
    ped['representante'] = Account.objects.get(id=ped['cliente']['representante_id']).__dict__['name']
    ped['data_criacao'] = ped['data_criacao'].strftime("%Y-%m-%d %H:%M:%S %Z")
    ped['data_liberacao'] = ped['data_liberacao'].strftime("%Y-%m-%d %H:%M:%S %Z")
    ped['ultima_atualiz'] = ped['ultima_atualiz'].strftime("%Y-%m-%d %H:%M:%S %Z")
    itens_pedido = list(PedidoItem.objects.filter(pedido_periodo__pedido__id=ped['id']).values(
        'pedido_periodo__periodo__periodo_faturamento','produto__produto','produto__tamanhos','qtds','desconto',
        'preco','qtd_item','valor_item'))
    for it in itens_pedido:
        it['periodo_faturamento'] = it['pedido_periodo__periodo__periodo_faturamento'].strftime("%Y-%m-%d")
        del it['pedido_periodo__periodo__periodo_faturamento']
        it['produto'] = it['produto__produto']
        del it['produto__produto']
        it['produto__tamanhos'] = json.loads(it['produto__tamanhos'])
        it['qtds'] = json.loads(it['qtds'])
        it['desconto'] = str(it['desconto'])
        it['preco'] = str(it['preco'])
        it['valor_item'] = str(it['valor_item'])
    ped['itens']=itens_pedido

    return ped


@api_view(['GET','POST'])
def pedidos_integracao(request):

    #View utilizada para integracao dos pedidos com o Linx
    
    if request.user.is_superuser:

        if request.method=='POST':
            pedido_id = request.POST['pedido_id']
            codigo_erp = request.POST['codigo_erp']
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.enviado_fabrica = True
            pedido.codigo_erp = codigo_erp
            pedido.save()
            return Response({'message': "Pedido Atualizado",'confirmed':True})
        else:
            pedidos = list(Pedido.objects.filter(liberado_rep=True,enviado_fabrica=False,is_teste=False).values())
            for ped in pedidos:
                ped = pedido_to_dict(ped)
            pedidos = json.dumps(pedidos)       
            return Response({'pedidos': pedidos,'confirmed':True})
    else:
        return Response({'message':'Usuario sem Permissao','confirmed':False})

@api_view(['GET'])
def pedidos(request):

    print(request.user.name)
    #View utilizada para consulta dos pedidos, diferencia entre representante e cliente

    if request.user.is_authenticated:
        if request.user.tipo_conta.is_rep:
            pedidos = Pedido.objects.select_related('cliente','user').filter(
                cliente__representante__login=request.user.login,liberado_cliente=True).order_by('-id')
        
        else:
            pedidos = Pedido.objects.select_related('cliente','user').filter(
                cliente__cnpj=request.user.login,liberado_cliente=True).order_by('-id')
        
        pedidos = pedidos.values('id','cliente__nome','cliente__desc_cond_pag',
        'cliente__razao_social','cliente__id','qtd_total','colecao',
                'valor_total','user__name','liberado_cliente','data_criacao','is_teste',
                'data_liberacao','liberado_rep','enviado_fabrica','codigo_erp')
        return Response({'pedidos':list(pedidos),'confirmed':True})
        # return Response({'pedidos':list(pedidos),'confirmed':True})
    
    else:
        return Response({'message':'Fazer Login','confirmed':False})
        # return Response({'message':'Fazer Login','confirmed':False})

@api_view(['GET','POST'])
def pedidos_save(request,id):

    #Salva Pedido - Somente liberacao cliente - Para ser finalizado depois
    pedido = Pedido.objects.get(id=id)
    if (request.user==pedido.user or request.user.login==pedido.cliente.representante.login):
        pedido.liberado_cliente=True
        if 'observacoes' in request.GET:
            observacoes = request.GET['observacoes']
        else:
            observacoes = ""
        if 'isTeste' in request.GET:
            is_teste = request.GET['isTeste']
            if is_teste == 'true':
                is_teste = True
            else:
                is_teste = False
        else:
            is_teste = False
        
        pedido.is_teste = is_teste
        pedido.observacoes = observacoes
        pedido.save()
        return Response({'message':'Pedido Salvo','confirmed':True})
    else:
        return Response({'message':'Fazer Login','confirmed':False})


@api_view(['GET','POST'])
def pedido_delete(request,id):

    # Deleta pedido caso o mesmo nao esteja pre-salvo(liberado cliente)
    pedido = Pedido.objects.get(id=id)

    if (request.user==pedido.user or request.user.login==pedido.cliente.representante.login):
        if pedido.liberado_cliente:
            return Response({'message':'Nao gerou exclusao - Pedido estava salvo','confirmed':True})
        else:
            pedido.delete()      
            return Response({'message':'Item excluida com sucesso','confirmed':True})
    else:
        return Response({'message':'nao foi possivel excluir','confirmed':False})


@api_view(['GET','POST'])
def pedidos_retoma(request,id):
    # Retoma Pedido, seta liberado_cliente para falso novamente
    pedido = Pedido.objects.get(id=id)
    if (request.user==pedido.user or request.user.login==pedido.cliente.representante.login):
        pedido.liberado_cliente=False
        pedido.save()
        if 'carrinhoAtualId' in request.GET:
            #Deleta carrinho atual caso nao esteja salvo (liberado_cliente)
            pedido_anterior = Pedido.objects.get(id=request.GET['carrinhoAtualId'])
            if not pedido_anterior.liberado_cliente:
                pedido_anterior.delete()
        return Response({'message':'Pedido Retomado','confirmed':True})
    else:
        return Response({'message':'Fazer Login','confirmed':False})

@api_view(['GET','POST'])
def pedidos_processa(request,id):
    # Processa pedido, fazendo verificacoes e separacao
    if request.method != 'GET':
        return Response({'message':'Somente GET requests','confirmed':False})
    if request.user.is_authenticated:
        pedido = Pedido.objects.get(id=id)
        if request.user.login == pedido.cliente.representante.login:                     
            status,response = pedidos_verifica(pedido)
            if not status:
                return response
            
            pedido.data_liberacao=datetime.now()
            is_teste = pedido.is_teste
            observacoes = pedido.observacoes
            pedido_copia = copy.copy(pedido.__dict__)      
            pedido_copia = pedido_to_dict(pedido_copia)
            lista_pedidos = pedido_separa(pedido)

            for ped in lista_pedidos:
                ped.data_liberacao=datetime.now()
                ped.liberado_rep=True
                ped.liberado_cliente=True
                ped.is_teste=is_teste
                ped.observacoes=observacoes
                # ped.observacoes=""
                ped.save()
            pedido_envia_email(pedido_copia,lista_pedidos)    
            return Response({'message':'Salvo com Sucesso','confirmed':True})
        else:         
            return Response({'message':'Usuario sem permissao','confirmed':False})
    else:
        return Response({'message':'Fazer Login','confirmed':False})

def pedido_envia_email(pedido,lista_pedidos):
    # Envia email do pedido
    destinatario = []
    if pedido['is_teste']:
        destinatario.append("comercial.greenish@grupoondas.com.br")
        destinatario.append("comercial@greenish.com.br")
        destinatario.append(pedido['cliente']['representante']['email'])
    else:
        destinatario.append(pedido['cliente']['email'])
        destinatario.append(pedido['cliente']['representante']['email'])
    file = pedido_pdf(pedido,lista_pedidos)
    email = EmailMessage(
        'Greenish - Copia de pedido automática', 'Copia do pedido em anexo.', 'Greenish <b2b@grupoondas.com.br>', destinatario)
    email.attach_file(file)
    email.send()
    os.remove(file)


def pedidos_verifica(pedido):
    #Verifica se existe periodo "Pre-Selecionado"
    periodos = PedidoPeriodo.objects.filter(pedido=pedido,periodo__is_provisorio=True)
    if len(periodos)>0:
        return False, Response({'message':'Nao e possivel finalizar com itens em periodo provisorio','confirmed':False})

    #Verifica Minimo
    embarque_minimo = Parametro.objects.get(parametro="EMBARQUE_MINIMO")
    embarque_minimo = int(embarque_minimo.valor)
    periodos = PedidoPeriodo.objects.filter(pedido=pedido,valor_periodo__lte=embarque_minimo)
    if len(periodos)>0:
        return False, Response({'message':'Valor do periodo nao poder ser menor que '+
        str(embarque_minimo)+'. Altere o pedido para continuar','confirmed':False})
    else:
        return True,'ok'

def pedido_separa(pedido):
    #Separa pedido por colecao, atribuindo tipo de venda dependendo da colecao vigente
    colecao_vigente = Parametro.objects.get(parametro="COLECAO_VIGENTE").valor

    cols = Pedido.objects.filter(id=pedido.id).values('pedidoperiodo__pedidoitem__produto__colecao').distinct()
    cols = [c['pedidoperiodo__pedidoitem__produto__colecao'] for c in cols]
    pedidos = []
    if len(cols)>1:
        for col in cols:
            #Cria novo pedido pra cada colecao
            tipo_venda = "COLEÇÃO NORMAL" if col==colecao_vigente else "SALDOS"
            novo_pedido = Pedido(cliente=pedido.cliente,user=pedido.user,tipo_venda=tipo_venda,colecao=col)
            novo_pedido.save()
                        
            periodos_mudar = PedidoPeriodo.objects.filter(pedido=pedido,pedidoitem__produto__colecao=col)

            for per in periodos_mudar:
                itens_alterar = PedidoItem.objects.filter(pedido_periodo=per,produto__colecao=col)
                novo_pedido_periodo,created = PedidoPeriodo.objects.get_or_create(periodo=per.periodo,pedido=novo_pedido)
                novo_pedido_periodo.save()
                itens_alterar.update(pedido_periodo=novo_pedido_periodo)
            
            novo_pedido.save()
            novo_pedido = pedido_atualiza_totais(novo_pedido.id)
            pedidos.append(novo_pedido)
        pedido.delete()
    else:
        col = cols[0]
        tipo_venda = "COLEÇÃO NORMAL" if col==colecao_vigente else "SALDOS"
        pedido.colecao=col
        pedido.tipo_venda=tipo_venda
        pedidos.append(pedido)
    
    return pedidos

def pedido_atualiza_totais(id_pedido):
    #atualiza periodos
    periodos = PedidoPeriodo.objects.filter(pedido__id=id_pedido)
    for per in periodos:
        totais = PedidoPeriodo.objects.filter(id=per.id).aggregate(qtd=Sum('pedidoitem__qtd_item'),valor=Sum('pedidoitem__valor_item'))
        per.qtd_periodo = totais['qtd']
        per.valor_periodo = totais['valor']
        per.save()
    #atualiza totais
    pedido = Pedido.objects.get(id=id_pedido)
    totais = Pedido.objects.filter(id=id_pedido).aggregate(qtd=Sum('pedidoperiodo__qtd_periodo'),valor=Sum('pedidoperiodo__valor_periodo'))
    pedido.qtd_total=totais['qtd']
    pedido.valor_total=totais['valor']
    pedido.save()
    return pedido

@api_view(['GET','POST'])
def promocoes_computa(request,id_pedido):
    pedido = Pedido.objects.get(id=id_pedido)
    id_promocao = request.GET['id_promocao']
    id_condicao = request.GET['id_condicao']
    if request.user.tipo_conta.is_rep and request.user.login == pedido.cliente.representante.login:
        promocao = Promocao.objects.get(id=id_promocao)
        promocao_condicao = PromocaoCondicao.objects.get(id=id_condicao)
        produtos_promo = list(PromocaoProduto.objects.filter(promocao=promocao).values('produto__produto'))
        produtos_promo = [p['produto__produto'] for p in produtos_promo]
        itens_pedido = PedidoItem.objects.filter(produto__produto__in=produtos_promo,pedido_periodo__pedido__id=id_pedido)
        totais_pedido = itens_pedido.aggregate(qtd=Sum('qtd_item'),valor=Sum('valor_item'))

             
        if promocao.tipo_condicao=='QTD':
            valor_atingido=totais_pedido['qtd']
        elif promocao.tipo_condicao=='VLR':
            valor_atingido=totais_pedido['valor']

        if valor_atingido>=promocao_condicao.condicao:
            if promocao.tipo_desconto=='VLR':
                for item in itens_pedido:
                    item.desconto = promocao_condicao.desconto
                    item.valor_item = round(item.preco-item.desconto,2)*item.qtd_item
                    item.save()
            elif promocao.tipo_desconto=='PCT':
                for item in itens_pedido:
                    item.desconto = promocao_condicao.desconto*item.preco
                    item.valor_item = round(item.preco-item.desconto,2)*item.qtd_item
                    item.save()
        
            pedido_atualiza_totais(id_pedido)
        return Response({'message': 'Promocoes Computadas','confirmed':True})
    else:
        return Response({'message': 'Usuario sem permissao','confirmed':False})


@api_view(['GET','POST'])
def promocoes_remove(request,id_pedido):
    # Retira promocoes que estavam aplicadas no pedido
    pedido = Pedido.objects.get(id=id_pedido)
    if request.user.tipo_conta.is_rep and request.user==pedido.user:

        itens_pedido = PedidoItem.objects.filter(desconto__gt=0,pedido_periodo__pedido__id=id_pedido)
        itens_pedido.update(desconto=0,valor_item=F('preco')*F('qtd_item'))
                     
        pedido_atualiza_totais(id_pedido)
        return Response({'message': 'Promocoes Removidas','confirmed':True})
    else:
        return Response({'message': 'Usuario sem permissao','confirmed':False})

@api_view(['GET','POST'])
def promocoes(request):
    # Consulta promocoes disponiveis
    if request.user.tipo_conta.is_rep:
        promocoes = Promocao.objects.all()
        lista_promocoes = []
        for prom in promocoes:
            dados_promo = {}
            dados_promo['descricao'] = prom.descricao
            dados_promo['tipo_condicao'] = prom.tipo_condicao
            dados_promo['tipo_desconto'] = prom.tipo_desconto
            dados_promo['id_promocao'] = prom.id
            promo_condicoes = PromocaoCondicao.objects.filter(promocao=prom)
            dados_promo['condicoes'] = list(
                promo_condicoes.values('id','condicao','desconto'))
            lista_promocoes.append(dados_promo)
        return Response({'promocoes':lista_promocoes,'message': 'OK','confirmed':True})
    else:
        return Response({'message': 'Usuario sem permissao','confirmed':False})

@api_view(['GET','POST'])
def categorias_update(request):
    # Consulta categorias    
    if request.user.is_superuser:
        if request.method == 'POST':
            cats = request.POST['cats']
            data_hora = timezone.now()
            dados_query, created = Categorias.objects.get_or_create(id=1)
            dados_query.dados = cats
            dados_query.atualizacao=data_hora
            dados_query.save()
            return Response({'message': 'Atualizado com Sucesso','confirmed':True})
    return Response({'message': 'Nao e superuser','confirmed':False})

def categorias(request):
    # Consulta categorias
    try:
        cats = Categorias.objects.get(id=1)
        cats = json.loads(cats.dados)
        return JsonResponse(cats,safe=False)
    except:
        return JsonResponse([],safe=False)

@api_view(['GET','POST'])
def clientes(request):
    # Consulta clientes do representante
    if request.user.is_authenticated:
        clientes = Cliente.objects.filter(representante__login=request.user.login,inativo=False).order_by('nome')
        return Response({'clientes':list(clientes.values()),'confirmed':True})
    else:
        return Response({'message': 'Fazer Login','confirmed':False})


@api_view(['GET','POST'])
def reps_users_update(request):
    # View para integracao dos usuarios com perfil de representante
    if request.user.is_superuser:
        if request.method == 'POST':
            reps = request.POST['reps']
            reps = json.loads(reps)          
            for r in reps:
                try:
                    representante = Account.objects.get(login=r['CNPJ'])
                    representante.email=r['EMAIL']
                except Account.DoesNotExist:
                    tipo_conta = AccountType.objects.get(tipo_conta="representante")
                    representante = Account(login=r['CNPJ'], name = r['REPRESENTANTE'],
                    tipo_conta=tipo_conta,email=r['EMAIL'])
                    representante.set_password(r['CNPJ'])
                representante.save()
        return Response({'message': 'Atualizado com Sucesso','confirmed':True})
    return Response({'message': 'Nao e superuser','confirmed':False})


@api_view(['GET','POST'])
def clientes_users_update(request):
    # View para integracao dos usuarios com perfil de cliente e cadastro de clientes
    if request.user.is_superuser:
        if request.method == 'POST':
            clientes = request.POST['clientes']
            clientes = json.loads(clientes)
            for c in clientes:

                #Cadastra Conta
                try:
                    conta = Account.objects.get(login=c['CNPJ'])
                    conta.email=c['EMAIL']
                except Account.DoesNotExist:
                    tipo_conta = AccountType.objects.get(tipo_conta="cliente")
                    conta = Account(login=c['CNPJ'], name = c['CLIENTE_ATACADO'],
                    tipo_conta=tipo_conta,email=c['EMAIL'])
                    conta.set_password(c['CNPJ'])
                conta.save()

                #Cadastra Cliente
                try:
                    representante = Account.objects.get(login=c['CNPJ_REP'])
                except:
                    representante = Account.objects.get(id=1)
                try:
                    cliente = Cliente.objects.get(cnpj=c['CNPJ'])
                    cliente.nome = c['CLIENTE_ATACADO']
                    cliente.razao_social=c['RAZAO_SOCIAL']
                    cliente.valor_aberto = c['VALOR_ABERTO']
                    cliente.tabela_precos = c['CODIGO_TAB_PRECO']
                    cliente.comissao = c['COMISSAO']
                    cliente.condicao_pagamento = c['CONDICAO_PGTO']
                    cliente.desc_cond_pag = c['DESC_COND_PGTO']
                    cliente.representante = representante
                    cliente.email = c['EMAIL']
                    cliente.telefone = c['TELEFONE']
                    cliente.whatsapp=c['WHATSAPP']
                    cliente.uf=c['UF']
                    cliente.cidade=c['CIDADE']
                    cliente.cep=c['CEP']
                    cliente.endereco=c['ENDERECO']                   
                except Cliente.DoesNotExist:
                    cliente = Cliente(cnpj=c['CNPJ'],nome=c['CLIENTE_ATACADO'],razao_social=c['RAZAO_SOCIAL'],comissao=c['COMISSAO'],
                    condicao_pagamento = c['CONDICAO_PGTO'],desc_cond_pag = c['DESC_COND_PGTO'],valor_aberto=c['VALOR_ABERTO'],
                    tabela_precos=c['CODIGO_TAB_PRECO'],representante=representante,
                    email=c['EMAIL'],telefone=c['TELEFONE'],whatsapp=c['WHATSAPP'],
                    uf=c['UF'],cidade=c['CIDADE'],cep=c['CEP'],endereco=c['ENDERECO'])
                cliente.save()
        data = date.today()
        data = date.strftime(data,'%Y-%m-%d')    
        ultima_atualizacao = Parametro.objects.get_or_create(parametro='ULTIMA_ATUALIZACAO_CLIENTES')[0]
        ultima_atualizacao.valor = data
        ultima_atualizacao.save()
        return Response({'message': 'Atualizado com Sucesso','confirmed':True})
    return Response({'message': 'Usuario nao e superuser','confirmed':False})

# def login_api(request):
    
#     if request.user.is_authenticated:
#         return Response({'sessionid': 'erro'})
    
#     if request.method == 'POST':
#         try:
#             username = request.POST['username']
#             password = request.POST['password']
#             user = authenticate(username=username, password=password)
#             login(request, user)
#             clienteId,clienteNome,isRep = verifica_session(request)
#             return Response({'sessionid': request.session.session_key,
#             'clienteId':clienteId,'clienteNome':clienteNome,
#             'isRep':isRep,'username':user.name,'message':'Login realizado com sucesso','confirmed':True})
#         except:
#             return Response({'message': 'Usuario ou senha Incorretos','confirmed':False})

def filterOptions(request):
    
    colecoes = list(ColecaoB2b.objects.filter(active=True).order_by('ordem').values_list('title', flat=True).distinct())
    periodos = list(Periodo.objects.filter(Q(periodo_faturamento__gt=date.today()) | Q(desc_periodo__in=['Imediato','30 dias'])).order_by(
                'periodo_faturamento').values_list('desc_periodo', flat=True).distinct())
    return JsonResponse({'colecoes': colecoes,'periodos':periodos})


@api_view(['GET'])
def login_api(request):
    
    if request.user.is_authenticated:

        colecoes = list(ColecaoB2b.objects.filter(active=True).order_by('ordem').values_list('title', flat=True).distinct())
        colecoes.insert(0, "Todas")
        periodos = list(Periodo.objects.filter(Q(periodo_faturamento__gt=date.today()) | Q(desc_periodo__in=['Imediato','30 dias'])).order_by(
                'periodo_faturamento').values_list('desc_periodo', flat=True).distinct())
        periodos.insert(0, "Todos")
        cats = Categorias.objects.get(id=1)
        cats = json.loads(cats.dados)

        clienteId,clienteNome,isRep = verifica_session(request)

        return Response({'sessionid': request.session.session_key,
        'clienteId':clienteId,'clienteNome':clienteNome,'isRep':isRep,
        'username':request.user.name,'colecoes':colecoes,'periodos':periodos,'cats':cats,
        'message':'Login realizado com sucesso','confirmed':True})
    else:
        return Response({'message':'Fazer Login','confirmed':False})

@api_view(['GET','POST'])
def logout_view(request):

    logout(request)
    return Response({'message':'Logout feito com sucesso','confirmed':True})

@api_view(['GET'])
def home(request):
    banners = list(Banner.objects.all().values().order_by('ordem'))
    return Response({'banners':banners})


@api_view(['GET','POST'])
def periodos_api(request):
    #Retorna as qtds disponiveis do produto para o periodo
    if request.user.is_authenticated:
        produto = request.GET['produto']
        periodo = request.GET['periodo']
        if periodo != '':
            dados = list(ProdutoPeriodo.objects.filter(produto__produto=produto,periodo__desc_periodo=periodo).values())
            if len(dados)>0:
                dados = dados[0]
                dados = json.loads(dados['dados'])   
                return Response({"dados":dados,'confirmed':True})
        
        return Response({"dados":[],'confirmed':True})

    else:
        return Response({'message':'Fazer Login','confirmed':False})


@api_view(['GET','POST'])
def produtos(request,linha,categoria,subcategoria=None):
    if request.user.is_authenticated:

        if 'clienteId' not in request.GET:
            return Response({'message':'Defina um cliente','confirmed':False})
            
        cliente = request.GET['clienteId']
        cliente =  Cliente.objects.get(id=cliente)
        
        tabela_precos = cliente.tabela_precos
        
        queryset = get_produtos(request,tabela_precos,linha,categoria,subcategoria)
        return Response({'lista':queryset})
           
    else:
        return Response({'message':'Fazer Login','confirmed':False})

@api_view(['GET','POST'])
def busca(request):
    if request.user.is_authenticated:

        if 'clienteId' not in request.GET:
            return Response({'message':'Defina um cliente','confirmed':False})           
        cliente = request.GET['clienteId']
        cliente =  Cliente.objects.get(id=cliente)
        tabela_precos = cliente.tabela_precos
        query = None
        if 'query' in request.GET:
            query = request.GET['query']
        queryset = busca_produtos(request,tabela_precos,query)
        return Response({'lista':queryset,'confirmed':True})
           
    else:
        return Response({'message':'Fazer Login','confirmed':False})

@api_view(['GET','POST'])
def produtos_update(request):

    #View para integracao de Produtos

    if request.user.is_superuser:
        if request.method == 'POST':
            #Altera campo ultima atualizacao
            data = date.today()
            data = date.strftime(data,'%Y-%m-%d') 
            ultima_atualizacao = Parametro.objects.get_or_create(parametro='ULTIMA_ATUALIZACAO_PRODUTOS')[0]
            ultima_atualizacao.valor = data
            ultima_atualizacao.save()


            produtos = request.POST['produtos']
            produtos = json.loads(produtos)

            errors_list = []
            
            for p in produtos:
                lista_periodos = json.dumps(p['lista_periodos'])
                #Cadastra Produto
                p['produto']['tams'] = json.dumps(p['produto']['tams'])
                try:
                    produto = Produto.objects.get(produto=p['produto']['produto'])
                    produto.descricao = p['produto']['descricao']
                    produto.sortido = p['produto']['sortido']
                    produto.composicao = p['produto']['composicao']
                    produto.linha = p['produto']['linha']
                    produto.categoria = p['produto']['categoria']
                    produto.subcategoria = p['produto']['subcategoria']
                    produto.url_imagem = p['produto']['url']
                    produto.qtd_tamanhos = p['produto']['qtd_tams']
                    produto.tamanhos = json.dumps(json.loads(p['produto']['tams']))
                    produto.colecao = p['produto']['colecao']
                    produto.periodos = lista_periodos
                    produto.precos = p['produto']['precos']

                except Produto.DoesNotExist:
                    produto = Produto(produto=p['produto']['produto'],descricao = p['produto']['descricao'],
                    sortido = p['produto']['sortido'],composicao = p['produto']['composicao'],linha=p['produto']['linha'],
                    categoria = p['produto']['categoria'],subcategoria = p['produto']['subcategoria'],
                    url_imagem = p['produto']['url'],qtd_tamanhos = p['produto']['qtd_tams'],
                    tamanhos = json.dumps(json.loads(p['produto']['tams'])),colecao = p['produto']['colecao'],
                    periodos = lista_periodos,precos = p['produto']['precos'])
                
                try:
                    produto.save()
                except:
                    errors_list.append(produto.produto)
                    continue
                
                precos = p['produto']['precos']
                for tabela in precos.keys():
                    try:
                        prod_preco = ProdutoPreco.objects.get(produto=produto,tabela=tabela)
                        prod_preco.preco = precos[tabela]
                    except:
                        prod_preco = ProdutoPreco(produto=produto,tabela=tabela,preco=precos[tabela])
                    prod_preco.save()
                periodos = p['periodos']
                prods_periodo_excluir = ProdutoPeriodo.objects.filter(produto__produto=produto).exclude(periodo__desc_periodo__in=lista_periodos)
                prods_periodo_excluir.delete()
                for periodo in periodos.keys():
                    try:
                        prod_periodo = ProdutoPeriodo.objects.get(produto__produto=produto,periodo__desc_periodo=periodo)
                        prod_periodo.dados = json.dumps(periodos[periodo])
                    except:
                        print(periodo)
                        periodo_obj = Periodo.objects.get(desc_periodo=periodo)
                        prod_periodo = ProdutoPeriodo(produto=produto,periodo=periodo_obj,dados = json.dumps(periodos[periodo]))
                    prod_periodo.save()
                
                #deleta ProdutosPeriodo fora dos da ultima atualizacao
                ProdutoPeriodo.objects.filter(produto__produto=produto).exclude(periodo__desc_periodo__in=periodos).delete()

        return Response({'message':'Atualizado com sucesso','errors':errors_list,'confirmed':True})
    return Response({'message':'Erro na atualizacao','confirmed':False})

@api_view(['GET','POST'])
def barras(request):
    # View para integracao de codigos de barras dos produtos
    if request.user.is_superuser:
        dados = request.POST['dados']
        dados = json.loads(dados)

        for d in dados:
            barras = d['barras']
            try:
                produto = Produto.objects.get(produto=d['produto'])
            except:
                continue
            
            for bar in barras:
                try:
                    produto_barra = ProdutoBarra.objects.get(produto=produto,barra=bar)
                except:
                    produto_barra = ProdutoBarra(produto=produto,barra=bar)
                    produto_barra.save()
        return Response({'message':'Atualizado com sucesso','confirmed':True})
    else:
        return Response({'message':'Erro na atualizacao','confirmed':False})




