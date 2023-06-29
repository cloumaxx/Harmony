from datetime import datetime
from imaplib import _Authenticator
from bson import ObjectId
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from pymongo import MongoClient
from harmonyApp.chatbot_functions.model_bert_multilingual_cased import obtener_respuesta
from harmonyApp.models import Comentarios, Credenciales, Usuario, Replicas
from harmonyProject.database import MongoDBConnection
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import ComentarioForm, LoginForm
from dateutil import parser
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage


# Create your views here.
db_connection = MongoDBConnection()


def pantalla_inicial(request, usuario_id):

    return render(request, "pantalla_inicial/pantalla_inicial.html", {"usuario_id": usuario_id})


"""
////////////////////////////////////////////////////////
////// Funciones enfocadas en los comentarios  /////////
////////////////////////////////////////////////////////
"""


def pantalla_foro(request, usuario_id):
    if request.method == 'POST':
        id_reda_Comet = usuario_id
        comentario_data = request.POST['comentario']
        likes = request.POST.getlist('likes')
        id_replicas = request.POST.getlist('id_replicas')

        comentario = Comentarios(
            id_reda_Comet=id_reda_Comet, comentario=comentario_data, likes=likes, id_replicas=id_replicas)

        comentario_dict = {
            'id_reda_Comet': comentario.id_reda_Comet,
            'comentario': comentario.comentario,
            'likes': comentario.likes,
            'id_replicas': comentario.id_replicas
        }

        db_connection.db.Comentarios.insert_one(comentario_dict)

        return redirect('pantalla_foro', usuario_id=usuario_id)

    # Obtener todos los comentarios de la base de datos
    comentarios = db_connection.db.Comentarios.find()

    # Crear el objeto Paginator

    comentarios_con_nombre_id = [(comentario, get_Nombre(comentario), str(
        comentario['_id'])) for comentario in comentarios]
    for comentario_tuple in comentarios_con_nombre_id:
        comentario2 = comentario_tuple[0]  # Extract the comment dictionary
        # Get the 'id_replicas' value (empty list if not present)
        id_replicas = comentario2.get('id_replicas', [])
        if len(id_replicas) > 0:
            new_id_replicas = []  # Lista para almacenar los nuevos valores de 'id_replicas'
            for j in id_replicas:
                # Obtiene el valor actualizado de 'id_replicas' usando la función get_inforeplicas
                new_id_replicas.append(get_inforeplicas(j))
            comentario2['id_replicas'] = new_id_replicas
    items_por_pagina = 2
    paginator = Paginator(comentarios_con_nombre_id, items_por_pagina)
    # Obtener el número de página a mostrar
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)
    cont = 0

    # ['id_replicas']
    return render(request, "pantalla_foro/pantalla_foro.html", {"usuario_id": usuario_id, "comentarios": page_obj})


def agregar_replica(request, usuario_id, comentario_id):
    if request.method == 'POST':
        replica_comentario = request.POST['replica']
        if len(replica_comentario) > 0:

            comentario = db_connection.db.Comentarios.find_one(
                {'_id': ObjectId(comentario_id)})
            id_replicas = comentario.get('id_replicas', [])

            if comentario:
                replica_dict = {
                    'idComentario': comentario_id,
                    'idRedactorReplica': usuario_id,
                    'contenidoReplica': replica_comentario,
                    'likes': []
                }

                insert_result = db_connection.db.Replicas.insert_one(
                    replica_dict)

                # Obtener el ID asignado a la réplica
                replica_id = insert_result.inserted_id
                id_replicas.append(replica_id)

                db_connection.db.Comentarios.update_one(
                    {'_id': ObjectId(comentario_id)},
                    {'$set': {'id_replicas': id_replicas}}
                )

        else:
            messages.error(request, 'Reply cannot be empty.')

    return redirect('pantalla_foro', usuario_id=usuario_id)


def incrementar_likes(request, usuario_id, comentario_id):

    if request.method == 'POST':
        # Obtener el comentario de la base de datos

        comentario = db_connection.db.Comentarios.find_one(
            {'_id': ObjectId(comentario_id)})

        if comentario:
            # Obtener los likes actuales del comentario
            likes = comentario.get('likes', [])
            if usuario_id not in likes:
                # Agregar el usuario_id a los likes
                likes.append(usuario_id)
            elif usuario_id in likes:
                likes.remove(usuario_id)
            # Actualizar los likes en la base de datos
            db_connection.db.Comentarios.update_one(
                {'_id': ObjectId(comentario_id)}, {'$set': {'likes': likes}})
    return redirect('pantalla_foro', usuario_id=usuario_id)


def get_inforeplicas(idReplica):
    replicas = db_connection.db.Replicas.find_one({'_id': ObjectId(idReplica)})
    try:

        nombreRedactor = db_connection.db.Usuario.find_one(
            {'_id': ObjectId(replicas['idRedactorReplica'])})['nombre']
        dic = {
            "nombreRedactor": nombreRedactor,
            "contenidoReplica": replicas['contenidoReplica'],
            "likes": replicas['likes']
        }
        return dic
    except:
        return None


def get_Nombre(comentario):

    user = db_connection.db.Usuario.find_one(
        {'_id': ObjectId(comentario['id_reda_Comet'])})
    try:
        return user['nombre']
    except:
        return None


def get_idComentario(comentario):

    user = db_connection.db.Usuario.find_one(
        {'_id': ObjectId(comentario['id_reda_Comet'])})
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

        comentario = Comentarios(
            id_reda_Comet=id_reda_Comet, comentario=comentario_data, likes=likes, id_replicas=id_replicas)

        comentario_dict = {
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

        db_connection.db.Comentarios.update_one(
            {'_id': ObjectId(comentario_id)},
            {'$set': {'comentario': nuevo_comentario}}
        )

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return HttpResponseBadRequest("Bad Request")


def borrar_comentario(request, usuario_id, comentario_id):
    if request.method == 'POST':
        # Eliminar el comentario de la base de datos

        db_connection.db.Comentarios.delete_one(
            {'_id': ObjectId(comentario_id)})

        return redirect('pantalla_foro', usuario_id=usuario_id)

    return HttpResponseBadRequest("Bad Request")


"""
/////////////////////////////////////////////////////
////// Funciones enfocadas en los usuarios  /////////
/////////////////////////////////////////////////////
"""


def pantalla_login(request):
    # Crear una instancia de la clase MongoDBConnection

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            clave = form.cleaned_data['clave']

            credenciales = db_connection.db.Credenciales
            user = credenciales.find_one({'correo': correo, 'clave': clave})

            if user is not None:
                user_id = str(user['_id'])
                # Cambia 'inicio' por la URL a la que deseas redirigir después del inicio de sesión
                return redirect('pantalla_inicial', usuario_id=user_id)
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
        usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo,
                          genero=genero, fecha_nacimiento=fecha_nacimiento)
        credenciales = Credenciales(correo=correo, clave=clave)

        # Obtener la conexión a la base de datos MongoDB

        # Guardar el usuario en la base de datos MongoDB
        usuario_dict = {
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'correo': usuario.correo,
            'genero': usuario.genero,
            'fecha_nacimiento': usuario.fecha_nacimiento,
        }

        result = db_connection.db.Usuario.insert_one(usuario_dict)
        usuario_cred = {
            # Convertir el ObjectId a una cadena de texto
            '_id': str(result.inserted_id),
            'correo': credenciales.correo,
            'clave': credenciales.clave,
        }
        db_connection.db.Credenciales.insert_one(usuario_cred)

        return redirect('pantalla_login')
    else:
        return render(request, 'pantalla_registro/pantalla_registro.html')


def pantalla_perfil_usuario(request, usuario_id):
    # Obtener la conexión a la base de datos MongoDB

    # Obtener el ID específico del usuario que deseas consultar
    usuario_dict = db_connection.db.Usuario.find_one(
        {'_id': ObjectId(usuario_id)})

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
        # Obtener todos los comentarios de la base de datos
        comentarios = db_connection.db.Comentarios.find(
            {'id_reda_Comet': usuario_id})
        comentarios_con_nombre_id = [(comentario, get_Nombre(comentario), str(
            comentario['_id'])) for comentario in comentarios]

        return render(request, 'pantalla_perfil_usuario/pantalla_perfil_usuario.html', {'usuario_id': usuario_id, 'usuario_obj': usuario_obj, "comentarios": comentarios_con_nombre_id})

    return HttpResponseBadRequest("Bad Request")


def editar_usuario(request, usuario_id):
    # Obtener el usuario específico que se desea actualizar

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        genero = request.POST.get('genero')

        fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
        fecha_nacimiento = datetime.strptime(
            fecha_nacimiento_str, "%Y-%m-%d").date()

        # Convertir el objeto datetime.date en datetime.datetime
        fecha_nacimiento = datetime.combine(
            fecha_nacimiento, datetime.min.time())

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
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # Si el método de la solicitud no es POST, renderizar la plantilla de edición de perfil
    return HttpResponseBadRequest("Bad Request")


"""
/////////////////////////////////////////////////////
//////   Funciones enfocadas en el chatbot  /////////
/////////////////////////////////////////////////////
"""


def pantalla_chatbot(request, usuario_id):
    contes = 0
    contes = contes + 1
    if request.method == 'POST':
        pregunta = request.POST.get('pregunta')
        contexto = "I am planning a picnic."
        respuesta = obtener_respuesta(pregunta, contexto)

        return render(request, "pantalla_chatbot/pantalla_chatbot.html", {"usuario_id": usuario_id, "respuesta": respuesta})

    return render(request, "pantalla_chatbot/pantalla_chatbot.html", {"usuario_id": usuario_id})

    """    
    if request.method == 'POST':
        id_reda_Comet = usuario_id
        comentario_data = request.POST['comentario']
        likes = request.POST.getlist('likes')
        id_replicas = request.POST.getlist('id_replicas')
        
        comentario = Comentarios(id_reda_Comet=id_reda_Comet, comentario=comentario_data, likes=likes, id_replicas=id_replicas)
        
        

        comentario_dict ={
            'id_reda_Comet': comentario.id_reda_Comet,
            'comentario': comentario.comentario,
            'likes': comentario.likes,
            'id_replicas': comentario.id_replicas
        }

        db_connection.db.Comentarios.insert_one(comentario_dict)

        return redirect('pantalla_chatbot', usuario_id=usuario_id)
    
    comentarios =  db_connection.db.Comentarios.find() # Obtener todos los comentarios de la base de datos
    comentarios_con_nombre_id = [(comentario, get_Nombre(comentario), str(comentario['_id'])) for comentario in comentarios]
    """
