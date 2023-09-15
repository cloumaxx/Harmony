from datetime import datetime
from bson import ObjectId
from django.http import  HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import  redirect, render
from harmonyApp.forms import LoginForm
from harmonyApp.models import Comentarios, Credenciales, Usuario
from harmonyApp.operations.imgru import actualizar_imagen, subir_imagen
from harmonyApp.operations.utils import  enviar_correo_inicio_sesion, get_Nombre, get_comentariosVer, get_img_perfil
from harmonyProject.database import MongoDBConnection
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from millyApp.views import send_to_rasa


# Create your views here.
db_connection = MongoDBConnection()
chat = []

def pantalla_inicial(request):
    return render(request,"pantalla_inicial\pantalla_incial.html")

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'id_user' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('pantalla_inicial')  # Redirigir a la página de inicio de sesión
    return wrapper

@login_required
def pantalla_menu_inicial(request,usuario_id ):
    return render(request, "pantalla_menu_inicial/pantalla_menu_inicial.html",{"usuario_id": usuario_id })
"""
////////////////////////////////////////////////////////
////// Funciones enfocadas en los comentarios  /////////
////////////////////////////////////////////////////////
"""
@login_required
def pantalla_foro(request,usuario_id,ordenar="mas likes"):
    ordenar = request.GET.get('ordenar', 'mas likes')  # Get the selected sorting option from the query parameters, defaulting to 'likes'

    if request.method == 'POST':
        id_reda_Comet = usuario_id
        comentario_data = request.POST['comentario']
        likes = request.POST.getlist('likes')
        replicas = []
        fechaPublicacion = datetime.now()
        comentario = Comentarios(
            id_reda_Comet=id_reda_Comet, comentario=comentario_data, likes=likes,fechaPublicacion = fechaPublicacion, replicas=replicas)
        comentario_dict = {
            'id_reda_Comet': comentario.id_reda_Comet,
            'comentario': comentario.comentario,
            'likes': comentario.likes,
            'fechaPublicacion' : fechaPublicacion,
            'replicas': comentario.replicas
        }

        db_connection.db.Comentarios.insert_one(comentario_dict)

        return redirect('pantalla_foro', usuario_id=usuario_id)

    if ordenar == 'mas reciente':
        comentarios = db_connection.db.Comentarios.find().sort([("fechaPublicacion", -1)])
    elif ordenar == 'mas antiguo':
        comentarios = db_connection.db.Comentarios.find().sort([("fechaPublicacion", 1)])
    elif ordenar == 'mas likes':
        comentarios = db_connection.db.Comentarios.find().sort([("likes", -1)])

    else:
        comentarios = db_connection.db.Comentarios.find().sort([("likes", 1)])

    # Crear el objeto Paginator
    items_por_pagina = 100
    paginator = Paginator(get_comentariosVer(comentarios,db_connection), items_por_pagina)
    # Obtener el número de página a mostrar
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    # ['id_replicas']
    return render(request, "pantalla_foro/pantalla_foro.html", {"usuario_id": usuario_id, "comentarios": page_obj,'ordenar': ordenar})

@login_required
def agregar_replica(request, usuario_id, comentario_id):
    if request.method == 'POST':
        replica_comentario = request.POST['replica']
        if len(replica_comentario) > 0:

            comentario = db_connection.db.Comentarios.find_one(
                {'_id': ObjectId(comentario_id)})
            
            if comentario:
                replicas = comentario.get('replicas', [])
                replica_dict = {
                    
                    'idRedactorReplica': usuario_id,
                    'contenidoReplica': replica_comentario,
                    'likes': []
                }
                replicas.append(replica_dict)
                # Obtener el ID asignado a la réplica
                #id_replicas.append(replica_id)

                db_connection.db.Comentarios.update_one(
                   {'_id': ObjectId(comentario_id)},
                  {'$set': {'replicas': replicas}}
                )

        else:
            messages.error(request, 'Reply cannot be empty.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def incrementar_likes_replica(request,usuario_id, comentario_id, pos):
    pos = int(pos) -1
    print("pos: ",pos,"comentario_id: ",comentario_id,usuario_id)
    
    if request.method == 'POST':
        # Obtener el comentario de la base de datos
        comentario = db_connection.db.Comentarios.find_one({'_id': ObjectId(comentario_id)})
        if comentario:
            replicas = comentario.get('replicas', [])
            replicaRevisar = replicas[pos]
            likesActuales = replicaRevisar.get('likes', [])
            print("->",likesActuales)
            if usuario_id not in likesActuales:
                likesActuales.append(usuario_id)
            else:
                likesActuales.remove(usuario_id)
            replicas[pos]['likes'] = likesActuales
            # Actualizar los likes en la base de datos
            db_connection.db.Comentarios.update_one({'_id': ObjectId(comentario_id)}, {'$set': {'replicas': replicas}})
            
       
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def incrementar_likes(request, usuario_id, comentario_id):
    if request.method == 'POST':
        # Obtener el comentario de la base de datos
        comentario = db_connection.db.Comentarios.find_one({'_id': ObjectId(comentario_id)})
        
        if comentario:
            # Obtener los likes actuales del comentario
            likes = comentario.get('likes', [])
            if usuario_id not in likes:
                # Agregar el usuario_id a los likes
                likes.append(usuario_id)
            elif usuario_id in likes:
                likes.remove(usuario_id)
            # Actualizar los likes en la base de datos
            db_connection.db.Comentarios.update_one({'_id': ObjectId(comentario_id)}, {'$set': {'likes': likes}})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def calificarApp(request, usuario_id):
    if request.method == 'POST':
        calificacion = request.POST.get('rating')
        # Obtener el comentario de la base de datos
        calificacionEntrante = db_connection.db.Calificacion.find_one({'id_usuario': usuario_id})
        idCalificacion = calificacionEntrante.get('_id')
        if calificacionEntrante:
            db_connection.db.Calificacion.update_one(
                {'_id': ObjectId(idCalificacion)},
                {
                    '$set': {
                        'calificacion': int(calificacion),
                        'fecha': datetime.now()
                    }
                }
            )
        else:
            calificacion_dict = {
                'id_usuario': usuario_id,
                'calificacion': int(calificacion),
                'fecha': datetime.now()
            }
            db_connection.db.Calificacion.insert_one(calificacion_dict)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
@login_required
def pantalla_nuevo_comentario(request, usuario_id):
    if request.method == 'POST':
        id_reda_Comet = usuario_id
        comentario_data = request.POST['comentario']
        likes = request.POST.getlist('likes')
        replicas = []
        comentario = Comentarios(id_reda_Comet=id_reda_Comet, comentario=comentario_data, likes=likes, replicas=replicas)

        comentario_dict ={
            'id_reda_Comet': comentario.id_reda_Comet,
            'comentario': comentario.comentario,
            'likes': comentario.likes,
            'replicas': comentario.replicas
        }

        db_connection.db.Comentarios.insert_one(comentario_dict)

         # Redirigir al perfil del usuario actualizado
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    return render(request, 'pantalla_foro/pantalla_nuevo_comentario.html', {'usuario_id': usuario_id})

@login_required
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

@login_required
def borrar_comentario(request, usuario_id, comentario_id):
    if request.method == 'POST':
        # Eliminar el comentario de la base de datos
        
        db_connection.db.Comentarios.delete_one({'_id': ObjectId(comentario_id)})
        
         # Redirigir al perfil del usuario actualizado
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    return HttpResponseBadRequest("Bad Request")

"""
/////////////////////////////////////////////////////
////// Funciones enfocadas en los usuarios  /////////
/////////////////////////////////////////////////////
"""

def pantalla_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            clave = form.cleaned_data['clave']

            credenciales = db_connection.db.Credenciales
            
            user = credenciales.find_one({'correo': correo, 'clave': clave})
            
            if user:
                user_id = str(user['_id'])
                nombre = db_connection.db.Usuario.find_one({'_id': ObjectId(user_id)})
                
                request.session['nombre'] = nombre['nombre']
                request.session['id_user'] = user_id
                return redirect('pantalla_menu_inicial',usuario_id=user_id)  # Cambia 'inicio' por la URL a la que deseas redirigir después del inicio de sesión
            else:
                form.add_error(None, 'Credenciales inválidas')
        else:
            form.add_error(None, 'Credenciales inválidas')

    else:
        form = LoginForm()
    return render(request, 'pantalla_login/pantalla_login.html', {'form': form})

def logout_view(request):
    # Eliminar el nombre de usuario de la sesión
    if 'id_user' in request.session:
        del request.session['id_user']
        del request.session['nombre']
    
    return redirect('pantalla_inicial')

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
        existeCorreo = db_connection.db.Credenciales.find_one({'correo': correo})
        if existeCorreo==None:
            #archivo = request.FILES.get('imagen_perfil')
            try:
                image = request.FILES['imagen_perfil']           
                val=subir_imagen(image.name, image.file)
                if val.status_code == 200:
                    json_img=val.json()
                    url_imagen_perfil = str(json_img['data']['link'])
                    code_delete_img = json_img['data']['deletehash']
                    
                else:
                    url_imagen_perfil = "https://i.imgur.com/0RW7b5J.jpg"
                    code_delete_img = ""
            except Exception as e:
            # Crear una instancia del modelo Usuario con los datos ingresados
                url_imagen_perfil = "https://i.imgur.com/0RW7b5J.jpg"
                code_delete_img = ""
            usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo, genero=genero, fecha_nacimiento=fecha_nacimiento, url_imagen_perfil=url_imagen_perfil,code_delete_img=code_delete_img,conversaciones=[])
            credenciales = Credenciales(correo=correo, clave=clave)
            # Guardar el usuario en la base de datos MongoDB
            usuario_dict = {
                        'nombre': usuario.nombre,
                        'apellido': usuario.apellido,
                        'correo': usuario.correo,
                        'genero': usuario.genero,
                        'fecha_nacimiento': usuario.fecha_nacimiento,
                        'url_imagen_perfil': usuario.url_imagen_perfil,
                        'code_delete_img': usuario.code_delete_img,
                        'conversaciones': usuario.conversaciones
            }
                    
            result = db_connection.db.Usuario.insert_one(usuario_dict)
            usuario_cred ={
                        '_id': str(result.inserted_id),  # Convertir el ObjectId a una cadena de texto
                        'correo': credenciales.correo,
                        'clave': credenciales.clave,
            }
            db_connection.db.Credenciales.insert_one(usuario_cred)
            enviar_correo_inicio_sesion(correo,  usuario.nombre + ' ' + usuario.nombre)
            return redirect('pantalla_login')
        else:
            error_message = "Correo ya existe"
            context = {'error_message': error_message}
        return render(request, 'pantalla_registro/pantalla_registro.html', context)

    else:
        return render(request, 'pantalla_registro/pantalla_registro.html')

@login_required
def pantalla_perfil_usuario(request,usuario_id):
  
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
            fecha_nacimiento=usuario_dict['fecha_nacimiento'],
            url_imagen_perfil=usuario_dict['url_imagen_perfil'],
        )
        comentarios =  db_connection.db.Comentarios.find({'id_reda_Comet': usuario_id}) # Obtener todos los comentarios de la base de datos
        comentarios_con_nombre_id = [(comentario, get_Nombre(comentario,db_connection),get_img_perfil(comentario,db_connection), str(comentario['_id'])) for comentario in comentarios]

        items_por_pagina = 2
        paginator = Paginator(comentarios_con_nombre_id, items_por_pagina)
        # Obtener el número de página a mostrar
        numero_pagina = request.GET.get('page')
        page_obj = paginator.get_page(numero_pagina)
        return render(request, 'pantalla_perfil_usuario/pantalla_perfil_usuario.html', {'usuario_id': usuario_id,'usuario_obj':usuario_obj, "comentarios": page_obj})
    
    return HttpResponseBadRequest("Bad Request")

@login_required    
def editar_usuario(request, usuario_id):
    # Obtener el usuario específico que se desea actualizar
    
    if request.method == 'POST':
        usuarioAux = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})
        code_delete_img_ante = usuarioAux['code_delete_img']    
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        genero = request.POST.get('genero')
        fecha_nacimiento_str = request.POST.get('fecha_nacimiento')
        fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
        fecha_nacimiento = datetime.combine(fecha_nacimiento, datetime.min.time())
        
        try:
            image = request.FILES['nueva_imagen_perfil']
            val=actualizar_imagen(code_delete_img_ante,image.name, image.file)
            if val.status_code == 200:
                json_img=val.json()
                url_imagen_perfil = str(json_img['data']['link'])
                code_delete_img = json_img['data']['deletehash']

                # Actualizar los datos del usuario en MongoDB
                db_connection.db.Usuario.update_one(
                    {'_id': ObjectId(usuario_id)},
                    {'$set': {
                        'nombre': nombre,
                        'apellido': apellido,
                        'correo': correo,
                        'genero': genero,
                        'fecha_nacimiento': fecha_nacimiento,
                        'url_imagen_perfil': url_imagen_perfil,
                        'code_delete_img': code_delete_img,
                    }}
                )
        except:
                db_connection.db.Usuario.update_one(
                    {'_id': ObjectId(usuario_id)},
                    {'$set': {
                        'nombre': nombre,
                        'apellido': apellido,
                        'correo': correo,
                        'genero': genero,
                        'fecha_nacimiento': fecha_nacimiento,
                        'url_imagen_perfil': usuarioAux['url_imagen_perfil'],
                        'code_delete_img': usuarioAux['code_delete_img'],
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
@login_required
def pantalla_chatbot(request, usuario_id,posicion=0):
    palabraBuscar = request.GET.get('palabraBuscar')
    if request.method == 'GET':
        if palabraBuscar != None and palabraBuscar != "":
            comentarios = db_connection.db.Comentarios.find({ 'comentario': { '$regex': str(palabraBuscar), '$options': 'i' } })
        else:
            comentarios = db_connection.db.Comentarios.find()
    # Crear el objeto Paginator
    
    items_por_pagina = 50
    paginator = Paginator(get_comentariosVer(comentarios,db_connection), items_por_pagina)
    # Obtener el número de página a mostrar
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    
    usuario_dict = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})
    url_imagen_perfil = usuario_dict['url_imagen_perfil']
    nombre_usuario = usuario_dict['nombre'] + " " + usuario_dict['apellido']
    conversaciones = usuario_dict['conversaciones']
    if len(conversaciones) == 0:
        conversaciones.append([])
        posicion = 0
        conversacion = conversaciones[posicion]
        db_connection.db.Usuario.update_one({'_id': ObjectId(usuario_id)}, {'$set': {'conversaciones': conversaciones}})

    else:
        posicion = posicion
        conversacion = conversaciones[posicion]
    return render(request, "pantalla_chatbot/pantalla_chatbot.html", {"usuario_id": usuario_id,"url_imagen_perfil":url_imagen_perfil,'nombre_usuario': nombre_usuario,"conversaciones": conversaciones,"conversacion":conversacion,"posicion":posicion, "comentarios": page_obj})

@login_required
def crearNuevoChat(request, usuario_id,posicion=0):
    if request.method == 'POST':
        # Obtener el usuario de la base de datos
        usuario = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})
        
        if usuario:
            # Obtener las conversaciones actuales del usuario
            conversaciones = usuario.get('conversaciones', [])
            
            # Agregar una nueva conversación vacía
            conversaciones.append([])
            # Actualizar las conversaciones en la base de datos
            db_connection.db.Usuario.update_one({'_id': ObjectId(usuario_id)}, {'$set': {'conversaciones': conversaciones}})
        return redirect('pantalla_chatbot', usuario_id=usuario_id,posicion=len(conversaciones)-1)

@login_required
def enviarMensajeChatBot(request,usuario_id,posicion=0):
    if request.method == 'POST':
        # Obtener el usuario de la base de datos
        usuario = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})
        
        if usuario:
            conversaciones = usuario.get('conversaciones', [])
            try:
                conversacion = conversaciones[posicion]
            except:
                conversacion = []
            pregunta = request.POST.get('pregunta')
            if pregunta == "" or pregunta == None or len(pregunta)==0:
                salida = "no entendi tu pregunta"
                #return render(request, "pantalla_chatbot/pantalla_chatbot.html", {"usuario_id": usuario_id})

            else:
                try:
                    respuestaChat = send_to_rasa(pregunta.lower())
                    salida = respuestaChat[0]['text']
                    print(respuestaChat)
                
                except:
                    salida = "no entendi tu pregunta"
                    
                nuevo_mensaje ={
                    'pregunta': pregunta,
                    'respuesta': salida}
                
                conversacion.append(nuevo_mensaje)
                db_connection.db.Usuario.update_one({'_id': ObjectId(usuario_id)}, {'$set': {'conversaciones': conversaciones}})
                mensaje_dict = {
                    
                    'mensaje' : pregunta,
                    'fecha' : datetime.now()
                }
                

                db_connection.db.Mensajes.insert_one(mensaje_dict)
        print('->',posicion)
        return redirect('pantalla_chatbot', usuario_id=usuario_id,posicion=posicion)
