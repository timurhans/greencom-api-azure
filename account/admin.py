# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (Account,AccountType)
from .forms import UserCreationForm, UserChangeForm


class AccountAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('login', 'name','tipo_conta', 'is_staff',  'is_superuser')
    # list_filter = ('is_superuser',)

    fieldsets = (
        (None, {'fields': ('login', 'is_staff', 'is_superuser','is_admin', 'password')}),
        ('Personal info', {'fields': ('name', 'tipo_conta','email')}),
        # ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('login', 'password1', 'password2','is_staff', 'is_superuser','is_admin')}),
        ('Personal info', {'fields': ('name','tipo_conta','email')}),
        # ('Groups', {'fields': ('groups',)}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )

    search_fields = ('login', 'name',)
    ordering = ('name',)
    # filter_horizontal = ()
    
    def password_change(self, request, extra_context=None):
        """
        Handles the "change password" task -- both form display and validation.
        """
        from django.contrib.admin.forms import AdminPasswordChangeForm
        from django.contrib.auth.views import password_change
        url = reverse('admin:password_change_done', current_app=self.name)
        defaults = {
            'current_app': self.name,
            'password_change_form': AdminPasswordChangeForm,
            'post_change_redirect': url,
            'extra_context': dict(self.each_context(request), **(extra_context or {})),
        }
        if self.password_change_template is not None:
            defaults['template_name'] = self.password_change_template
        return password_change(request, **defaults)


   


admin.site.register(Account, AccountAdmin)
admin.site.register(AccountType)