from datetime import datetime
from imaplib import _Authenticator
from bson import ObjectId
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from pymongo import MongoClient
from harmonyApp.models import Credenciales, Usuario
from harmonyProject.database import MongoDBConnection
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm
from dateutil import parser


# Create your views here.

def pantalla_inicial(request,usuario_id ):
    return render(request, "pantalla_inicial/pantalla_inicial.html",{"usuario_id": usuario_id })

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
                return redirect('pantalla_inicial',usuario_id=user_id)  # Cambia 'inicio' por la URL a la que deseas redirigir después del inicio de sesión
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
        fecha_nacimiento_str = request.POST.get('fecha_nacimiento')

        # Convertir la cadena de fecha en un objeto de tipo datetime
        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d')

        # Crear una instancia del modelo Usuario con los datos ingresados
        usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo, genero=genero, fecha_nacimiento=fecha_nacimiento)
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

        return redirect('pantalla_login')
    else:
        return render(request, 'pantalla_registro/pantalla_registro.html')

def pantalla_perfil_usuario(request,usuario_id):
    #
    # Obtener la conexión a la base de datos MongoDB
    db_connection = MongoDBConnection()
    
    # Obtener el ID específico del usuario que deseas consultar
    usuario_dict = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})

    # Verificar si se encontró un usuario con el ID especificado
    if usuario_dict:
        # Crear una instancia del modelo Usuario con los datos obtenidos
        usuario_obj = Usuario(
            id=usuario_dict['_id'],
            nombre=usuario_dict['nombre'],
            apellido=usuario_dict['apellido'],
            correo=usuario_dict['correo'],
            genero=usuario_dict['genero'],
            fecha_nacimiento=usuario_dict['fecha_nacimiento']
        )
        #print(usuario_obj)
        # Imprimir los datos del usuario
        return render(request, 'pantalla_perfil_usuario/pantalla_perfil_usuario.html', {'usuario_id': usuario_obj})
    else:

        print("No se encontró ningún usuario con el ID especificado.")
        return render(request, "pantalla_perfil_usuario/pantalla_perfil_usuario.html",{'usuario_id': usuario_id})
    

def actualizar_usuario(request, usuario_id):
    # Obtener el usuario específico que se desea actualizar
    db_connection = MongoDBConnection()
    usuario_dict = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})

    if not usuario_dict:
        # Si no se encuentra el usuario, mostrar un mensaje de error o redireccionar a alguna otra página.
        return HttpResponse("No se encontró el usuario con el ID especificado.")

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        genero = request.POST.get('genero')
        
        fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()

        # Convertir el objeto datetime.date en datetime.datetime
        fecha_nacimiento = datetime.combine(fecha_nacimiento, datetime.min.time())

        # Actualizar los datos del usuario en MongoDB
        db_connection.db.Usuario.update_one(
            {'_id': ObjectId(usuario_id)},
            {'$set': {
                'nombre': nombre,
                'apellido': apellido,
                'correo': correo,
                'genero': genero,
                'fecha_nacimiento': fecha_nacimiento
            }}
        )

        # Redirigir al perfil del usuario actualizado
        return redirect('pantalla_perfil_usuario', usuario_id=usuario_id)

    # Si el método de la solicitud no es POST, renderizar la plantilla de edición de perfil
    return render(request, 'pantalla_perfil_usuario/pantalla_editar_perfil.html', {'usuario_id': usuario_dict})