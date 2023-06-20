from datetime import datetime
from imaplib import _Authenticator
from bson import ObjectId
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from pymongo import MongoClient
from harmonyApp.models import Comentarios, Credenciales, Usuario
from harmonyProject.database import MongoDBConnection
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import ComentarioForm, LoginForm
from dateutil import parser
from django.contrib import messages


# Create your views here.

def pantalla_inicial(request,usuario_id ):
    
    return render(request, "pantalla_inicial/pantalla_inicial.html",{"usuario_id": usuario_id })
"""
////////////////////////////////////////////////////////
////// Funciones enfocadas en los comentarios  /////////
////////////////////////////////////////////////////////
"""
def pantalla_foro(request,usuario_id):
    print("::>>",type(usuario_id),usuario_id)
    db_connection = MongoDBConnection()
    if request.method == 'POST':
        id_reda_Comet = usuario_id
        comentario_data = request.POST['comentario']
        likes = request.POST.getlist('likes')
        id_replicas = request.POST.getlist('id_replicas')
        
        comentario = Comentarios(id_reda_Comet=id_reda_Comet, comentario=comentario_data, likes=likes, id_replicas=id_replicas)
        
        db_connection = MongoDBConnection()

        comentario_dict ={
            'id_reda_Comet': comentario.id_reda_Comet,
            'comentario': comentario.comentario,
            'likes': comentario.likes,
            'id_replicas': comentario.id_replicas
        }

        db_connection.db.Comentarios.insert_one(comentario_dict)

        return redirect('pantalla_foro', usuario_id=usuario_id)
    
    comentarios =  db_connection.db.Comentarios.find() # Obtener todos los comentarios de la base de datos
    comentarios_con_nombre_id = [(comentario, get_Nombre(comentario), str(comentario['_id'])) for comentario in comentarios]
    return render(request, "pantalla_foro/pantalla_foro.html", {"usuario_id": usuario_id, "comentarios": comentarios_con_nombre_id})


def incrementar_likes(request, usuario_id, comentario_id):
    
    if request.method == 'POST':
        # Obtener el comentario de la base de datos
        db_connection = MongoDBConnection()
        comentario = db_connection.db.Comentarios.find_one({'_id': ObjectId(comentario_id)})
        
        if comentario:
            # Obtener los likes actuales del comentario
            likes = comentario.get('likes', [])
            
            # Verificar si el usuario ya ha dado like al comentario
            if usuario_id not in likes:
                # Agregar el usuario_id a los likes
                likes.append(usuario_id)
                
                # Actualizar los likes en la base de datos
                db_connection.db.Comentarios.update_one({'_id': ObjectId(comentario_id)}, {'$set': {'likes': likes}})
    
    # Redirigir a la página de pantalla_foro
    return redirect('pantalla_foro', usuario_id=usuario_id)

def get_Nombre(comentario):
    db_connection = MongoDBConnection()
    user = db_connection.db.Usuario.find_one({'_id': ObjectId(comentario['id_reda_Comet'])})
    try:
        return user['nombre']
    except user.DoesNotExist:
        return None

def get_idComentario(comentario):
    db_connection = MongoDBConnection()
    user = db_connection.db.Usuario.find_one({'_id': ObjectId(comentario['id_reda_Comet'])})
    try:
        return user['id']
    except user.DoesNotExist:
        return None
    
def pantalla_nuevo_comentario(request, usuario_id):
    if request.method == 'POST':
        id_reda_Comet = usuario_id
        comentario_data = request.POST['comentario']
        likes = request.POST.getlist('likes')
        id_replicas = request.POST.getlist('id_replicas')
        
        comentario = Comentarios(id_reda_Comet=id_reda_Comet, comentario=comentario_data, likes=likes, id_replicas=id_replicas)
        
        db_connection = MongoDBConnection()

        comentario_dict ={
            'id_reda_Comet': comentario.id_reda_Comet,
            'comentario': comentario.comentario,
            'likes': comentario.likes,
            'id_replicas': comentario.id_replicas
        }

        db_connection.db.Comentarios.insert_one(comentario_dict)

        return redirect('pantalla_foro', usuario_id=usuario_id)

    return render(request, 'pantalla_foro/pantalla_nuevo_comentario.html', {'usuario_id': usuario_id})


def editar_comentario(request, usuario_id, comentario_id):
    if request.method == 'POST':
        nuevo_comentario = request.POST['comentario']
        
        # Actualizar el comentario en la base de datos
        db_connection = MongoDBConnection()
        db_connection.db.Comentarios.update_one(
            {'_id': ObjectId(comentario_id)},
            {'$set': {'comentario': nuevo_comentario}}
        )
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    return HttpResponseBadRequest("Bad Request")

def borrar_comentario(request, usuario_id, comentario_id):
    if request.method == 'POST':
        # Eliminar el comentario de la base de datos
        db_connection = MongoDBConnection()
        db_connection.db.Comentarios.delete_one({'_id': ObjectId(comentario_id)})
        
        return redirect('pantalla_foro', usuario_id=usuario_id)
    
    return HttpResponseBadRequest("Bad Request")
"""
/////////////////////////////////////////////////////
////// Funciones enfocadas en los usuarios  /////////
/////////////////////////////////////////////////////
"""


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
    print(usuario_id)
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
        comentarios =  db_connection.db.Comentarios.find({'id_reda_Comet': usuario_id}) # Obtener todos los comentarios de la base de datos
        comentarios_con_nombre_id = [(comentario, get_Nombre(comentario), str(comentario['_id'])) for comentario in comentarios]
    
        return render(request, 'pantalla_perfil_usuario/pantalla_perfil_usuario.html', {'usuario_id': usuario_id,'usuario_obj':usuario_obj, "comentarios": comentarios_con_nombre_id})
    
    return HttpResponseBadRequest("Bad Request")
    
def actualizar_usuario(request, usuario_id):
    db_connection = MongoDBConnection()
    usuario_dict = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})

    if request.method == 'POST':
        # Obtener los datos actualizados del formulario
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        genero = request.POST.get('genero')
        fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
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

        messages.success(request, 'Usuario actualizado correctamente.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # Si el método de la solicitud no es POST, renderizar el perfil del usuario en el modal
    return HttpResponseBadRequest("Bad Request")
