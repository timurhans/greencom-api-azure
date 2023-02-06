"""ecomb2b URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.shortcuts import redirect
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from core.views import (logout_view,login_api,clientes_users_update,
reps_users_update,pedidos,pedidos_save,pedidos_integracao,
pedidos_processa,pedidos_retoma,pedido_delete,pedidos_gera_pdf,
promocoes,promocoes_computa,promocoes_remove,
# generate_PDF,pedidos,
produtos,produtos_online,home,clientes,busca,get_produtos_com_disp_periodo,
categorias,categorias_update,periodos_api,barras,carrinho,carrinho_update_periodo,carrinho_update_qtds,
carrinho_delete_item,produtos_update,produtos_cadastra_promo,produtos_lista,pedido_view_get,pedidos_atualiza_entregar,
get_pedidos_atualizar_entregar,get_materiais_trade,save_solicitacao_trade,get_solicitacoes_trade,get_dados_extras_clientes)
from params.views import (params,filterOptions,update_last_update_integrador)
from account.views import RegistrationView, ProfileView,change_password
from rest_framework.authtoken.views import obtain_auth_token


admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    path('home/', home),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('', home),
    path('admin/', admin.site.urls),
    path('carrinho/', carrinho),
    path('busca/', busca),
    path('carrinho/delete_item/<id>/', carrinho_delete_item),
    path('carrinho/update_periodo/<id>/', carrinho_update_periodo),
    path('carrinho/update_qtds/<id>/', carrinho_update_qtds),
    path('pedidos/', pedidos),
    path('pedidos/deleta/<id>/', pedido_delete),
    path('pedidos/salva/<id>/', pedidos_save),
    path('pedidos/gera_pdf/<id>/', pedidos_gera_pdf),
    path('pedidos/retoma/<id>/', pedidos_retoma),
    path('pedidos/processa/<id>/', pedidos_processa),
    path('pedido/<idPedido>/', pedido_view_get),
    path('pedidos_integracao/', pedidos_integracao),
    path('pedidos_integracao_entregar/', pedidos_atualiza_entregar),
    path('get_pedidos_integracao_entregar/', get_pedidos_atualizar_entregar),
    path('trade/get_materiais', get_materiais_trade),
    path('trade/get_solicitacoes', get_solicitacoes_trade),
    path('trade/salva_solicitacao', save_solicitacao_trade),
    path('dados/dados_extras_clientes', get_dados_extras_clientes),
    path('promocoes', promocoes),
    path('promocoes/', promocoes),
    path('promocoes/<id_cliente>', promocoes),
    path('promocoes/<id_pedido>/', promocoes_computa),
    path('promocoes/remove/<id_pedido>/', promocoes_remove),
    # path('pedidos/<id_pedido>/PDF/', generate_PDF),
    path('periodos/', periodos_api),
    path('login/', login_api,name='login_api'),
    path('produtos_update/', produtos_update),
    path('produtos_cadastra_promo/', produtos_cadastra_promo),
    path('barras/', barras),
    path('params/', params),
    path('filterOptions/', filterOptions),
    path('clientes_users_update/', clientes_users_update),
    path('reps_users_update/', reps_users_update),
    path('clientes/', clientes,name='clientes'),
    path('categorias/', categorias,name='categorias'),
    path('categorias_update/', categorias_update),
    path('produtos_com_disp_periodo/', get_produtos_com_disp_periodo),
    path('update_last_update_integrador/', update_last_update_integrador),
    path('change_password/', change_password),

    path('accounts/', RegistrationView.as_view(), name='register'),
    path('accounts/register/', RegistrationView.as_view(), name='register'),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', logout_view,name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('lista/<lista>/', produtos_lista,name='produtos_lista'),
    path('online/', produtos_online,name='produtos_online'),
    path('<linha>/<categoria>/', produtos,name='produtos'),
    path('<linha>/<categoria>/<subcategoria>/', produtos,name='produtos'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)