from django import forms

from harmonyApp.models import Comentarios

class LoginForm(forms.Form):
    correo = forms.EmailField()
    clave = forms.CharField(widget=forms.PasswordInput)

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentarios
        fields = ['id_reda_Comet', 'comentario', 'likes', 'id_replicas']
