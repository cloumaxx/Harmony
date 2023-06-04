from django.shortcuts import redirect, render
from pymongo import MongoClient
from harmonyApp.models import Usuario
from harmonyProject.database import MongoDBConnection

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

        # Obtener la conexión a la base de datos MongoDB
        db_connection = MongoDBConnection()

        # Guardar el usuario en la base de datos MongoDB
        usuario_dict = {
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'correo': usuario.correo,
            'clave': usuario.clave,
            'edad': usuario.edad,
        }
        db_connection.db.usuarios.insert_one(usuario_dict)

        return redirect('pantalla_inicial')
    else:
        return render(request, 'pantalla_registro/pantalla_registro.html')
