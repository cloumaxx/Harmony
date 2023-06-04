from django.shortcuts import redirect, render
from pymongo import MongoClient

from harmony_app.models import Usuario

# Create your views here.

def pantalla_inicial(request):
    return render(request, "pantalla_inicial/pantalla_inicial.html")

def pantalla_login(request):
    return render(request, "pantalla_login/pantalla_login.html")

def pantalla_registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        clave = request.POST.get('clave')
        edad = request.POST.get('edad')

        # Crear una instancia del modelo Usuario con los datos ingresados
        usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo, clave=clave, edad=edad)
        
        # Guardar el usuario en la base de datos MongoDB
        client = MongoClient('<mongodb_connection_string>')
        db = client['<database_name>']
        usuarios_collection = db['usuarios']
        usuarios_collection.insert_one(usuario.__dict__)

        return redirect('pantalla_inicial')
    else:
        return render(request, 'pantalla_registro/pantalla_registro.html')
