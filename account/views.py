from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.http import JsonResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse

from .models import Account
from .forms import RegistrationForm

import json

class RegistrationView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm

    def get_context_data(self, *args, **kwargs):
        context = super(RegistrationView, self).get_context_data(*args, **kwargs)
        context['next'] = self.request.GET.get('next')
        return context

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        success_url = reverse('login')
        if next_url:
            success_url += '?next={}'.format(next_url)

        return success_url


class ProfileView(UpdateView):
    model = Account
    fields = ['login','name']
    template_name = 'registration/profile.html'

    def get_success_url(self):
        return reverse('home')

    def get_object(self):
        return self.request.user


def change_password(request):
    post = request.body
    post = post.decode("utf-8").replace("'", '"')
    post = json.loads(post)
    senhaAtual = post['senhaAtual']
    senhaNova = post['senhaNova']
    user = request.user
    if user.check_password(senhaAtual):      
        user.set_password(senhaNova)
        user.save()
        return JsonResponse({'message':'Alterado com Sucesso','confirmed':True})
    else:
        return JsonResponse({'message':'Senha Atual nao confere','confirmed':False})