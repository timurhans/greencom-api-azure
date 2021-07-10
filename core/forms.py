from django import forms

class LoginForm(forms.Form):
    user = forms.CharField(required=True,label='Login')
    password = forms.CharField(required=True,widget=forms.PasswordInput,label='Senha')