from django import forms

class LoginForm(forms.Form):
    correo = forms.EmailField()
    clave = forms.CharField(widget=forms.PasswordInput)
