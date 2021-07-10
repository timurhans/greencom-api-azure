from django.contrib import admin

# Register your models here.

from .models import (ColecaoB2b,ColecaoErp,Banner,Periodo,Parametro)

class PeriodoAdmin(admin.ModelAdmin):

    list_display = ('desc_periodo','periodo_faturamento','periodo_vendas')

    ordering = ('periodo_faturamento',)
    filter_horizontal = ()

class ParametroAdmin(admin.ModelAdmin):

    list_display = ('parametro','valor')

    ordering = ('parametro',)
    filter_horizontal = ()

admin.site.register(Parametro,ParametroAdmin)
admin.site.register(ColecaoB2b)
admin.site.register(ColecaoErp)
admin.site.register(Banner)
admin.site.register(Periodo,PeriodoAdmin)

