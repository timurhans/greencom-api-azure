from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from django.utils import timezone
# Create your models here.



class AccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, login,name, password, **extra_fields):
        values = [login]
        field_value_map = dict(zip(self.model.REQUIRED_FIELDS, values))
        for field_name, value in field_value_map.items():
            if not value:
                raise ValueError('The {} value must be set'.format(field_name))

        user = self.model(
            login=login,
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, login,name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_admin', False)
        return self._create_user(login,name, password, **extra_fields)

    def create_superuser(self, login,name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(login,name, password, **extra_fields)

class AccountType(models.Model):
    tipo_conta = models.CharField(max_length=30,unique=True,null=False)
    is_rep = models.BooleanField(default=False)
    salva_pedido = models.BooleanField(default=False)
    libera_pedido = models.BooleanField(default=False)
    def __str__(self):
        return str(self.tipo_conta)


class Account(AbstractBaseUser, PermissionsMixin):


    login = models.CharField(max_length=30,unique=True,null=False)
    name = models.CharField(max_length=150,unique=False,null=False)
    tipo_conta = models.ForeignKey(AccountType,null=True,blank=True, on_delete=models.CASCADE)
    email = models.EmailField(default="",blank=True,null=True)
    
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True)

    objects = AccountManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

    def has_perm(self,perm,obj=None):
        return self.is_admin
    def has_module_perms(self,app_label):
        return True


