import datetime
from imaplib import _Authenticator
from bson import ObjectId
from django.http import HttpResponse
from django.shortcuts import redirect, render
from pymongo import MongoClient
from harmonyApp.models import Credenciales, Usuario
from harmonyProject.database import MongoDBConnection
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm

# Create your views here.

def pantalla_inicial(request,id):
    return render(request, "pantalla_inicial/pantalla_inicial.html",{"id": id})

def pantalla_login(request):
    db_connection = MongoDBConnection()  # Crear una instancia de la clase MongoDBConnection

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            clave = form.cleaned_data['clave']
            
            db_connection = MongoDBConnection()
            credenciales = db_connection.db.Credenciales
            user = credenciales.find_one({'correo': correo, 'clave': clave})
            
            if user is not None:
                user_id = str(user['_id'])
                return redirect('pantalla_inicial',id=user_id)  # Cambia 'inicio' por la URL a la que deseas redirigir después del inicio de sesión
            else:
                form.add_error(None, 'Credenciales inválidas')
    else:
        form = LoginForm()
    return render(request, 'pantalla_login/pantalla_login.html', {'form': form})


def pantalla_registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        clave = request.POST.get('clave')
        genero = request.POST.get('genero')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        # Crear una instancia del modelo Usuario con los datos ingresados
        usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo,genero=genero, fecha_nacimiento=fecha_nacimiento)
        credenciales = Credenciales(correo=correo, clave=clave)
        # Obtener la conexión a la base de datos MongoDB
        db_connection = MongoDBConnection()

        # Guardar el usuario en la base de datos MongoDB
        usuario_dict = {
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'correo': usuario.correo,
            'genero': usuario.genero,
            'fecha_nacimiento': usuario.fecha_nacimiento,
        }
        
        result = db_connection.db.Usuario.insert_one(usuario_dict)
        usuario_cred ={
            '_id': str(result.inserted_id),  # Convertir el ObjectId a una cadena de texto
            'correo': credenciales.correo,
            'clave': credenciales.clave,
        }
        db_connection.db.Credenciales.insert_one(usuario_cred)

        return redirect('pantalla_inicial')
    else:
        return render(request, 'pantalla_registro/pantalla_registro.html')

def pantalla_perfil_usuario(request,usuario_id):
    #
    # Obtener la conexión a la base de datos MongoDB
    db_connection = MongoDBConnection()

    # Obtener el ID específico del usuario que deseas consultar
    usuario_dict = db_connection.db.usuarios.find_one({'_id': ObjectId(usuario_id)})

    # Verificar si se encontró un usuario con el ID especificado
    if usuario_dict:
        # Crear una instancia del modelo Usuario con los datos obtenidos
        usuario_obj = Usuario(
            id=usuario_dict['_id'],
            nombre=usuario_dict['nombre'],
            apellido=usuario_dict['apellido'],
            correo=usuario_dict['correo'],
            clave=usuario_dict['clave'],
            genero=usuario_dict['genero'],
            fecha_nacimiento=usuario_dict['fecha_nacimiento']
        )
        print(usuario_obj)
        # Imprimir los datos del usuario
        return render(request, 'pantalla_perfil_usuario/pantalla_perfil_usuario.html', {'usuario_id': usuario_obj})
    else:

        print("No se encontró ningún usuario con el ID especificado.")
        return render(request, "pantalla_perfil_usuario/pantalla_perfil_usuario.html",{'usuario_id': usuario_id})
    
def actualizar_usuario(request, usuario_id):
    usuario_id = "647ff20bcf493386707c470a"

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        clave = request.POST.get('clave')
        fecha_nacimiento = datetime.strptime(request.POST.get('fecha_nacimiento'), '%Y-%m-%d').date()

        try:
            # Obtener el usuario de la base de datos
            usuario = Usuario.objects.get(id=usuario_id)

            # Actualizar los datos del usuario con los valores ingresados
            usuario.nombre = nombre
            usuario.apellido = apellido
            usuario.correo = correo
            usuario.clave = clave
            usuario.fecha_nacimiento = fecha_nacimiento

            # Guardar los cambios en la base de datos
            usuario.save()

            # Redirigir al perfil del usuario actualizado
            return redirect('pantalla_perfil_usuario', usuario_id=usuario.id)

        except Usuario.DoesNotExist:
            # Si no se encuentra el usuario, mostrar un mensaje de error o redirigir a otra página
            return HttpResponse("El usuario no existe.")
    else:
        # Si el método de la solicitud no es POST, redirigir a otra página o mostrar un mensaje de error
        return HttpResponse("Método no permitido.")