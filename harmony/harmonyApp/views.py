from datetime import datetime
from bson import ObjectId
from django.http import  HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import  redirect, render
from harmonyApp.forms import LoginForm
from harmonyApp.models import Comentarios, Credenciales, Usuario
from harmonyApp.operations.imgru import actualizar_imagen, subir_imagen
from harmonyApp.operations.utils import  cifrarClaves, comunicacionMillyApi, decifrarClaves, eliminar_tildes, get_comentariosVer
from harmonyProject.database import MongoDBConnection
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import pandas as pd
import plotly.express as px
import plotly.offline as opy
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from bson import ObjectId, errors
import matplotlib.colors as mcolors
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


# Create your views here.
db_connection = MongoDBConnection()
chat = []

def pantalla_inicial(request):
    logout_view(request)
    return render(request,"pantalla_inicial/pantalla_incial.html")

def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'id_user' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('pantalla_inicial')  # Redirigir a la página de inicio de sesión
    return wrapper

@login_required
def pantalla_menu_inicial(request,usuario_id ):

    return render(request, "pantalla_menu_inicial/pantalla_menu_inicial.html",{"usuario_id": usuario_id})
"""
////////////////////////////////////////////////////////
////// Funciones enfocadas en las estadisticas  ////////
////////////////////////////////////////////////////////
"""
@login_required
def pantalla_estadisticas(request, usuario_id):
    try:
        usuario_id = ObjectId(str(request.session['id_user']))
        usuarios_cursor = db_connection.db.Usuario.find()
        cantidad_usuarios = sum(1 for _ in usuarios_cursor)
        
        # Obtener mensajes más comunes
        mensajes_cursor = db_connection.db.Mensajes.find()
        df = pd.DataFrame(mensajes_cursor)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Agregar una columna de fecha sin la hora para agrupar por día
        df['fecha_dia'] = df['fecha'].dt.floor('d')  # Redondear a la fecha más cercana
        
        # Contar la cantidad de mensajes por día
        mensajes_por_dia = df.groupby('fecha_dia').size()
        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        # Crear gráfico de barras con Plotly
       # Crear gráfico de barras con Plotly y ajustar el espaciado entre barras
        fig = px.bar(x=mensajes_por_dia.index, y=mensajes_por_dia.values, labels={'x': 'Fecha', 'y': 'Cantidad de Mensajes'})
        fig.update_layout(title='Mensajes Enviados a Milly', xaxis_title='Fecha', yaxis_title='Cantidad de Mensajes', plot_bgcolor='rgba(0,0,0,0)', title_x=0.5) # Establecer un color de fondo para el gráfico
        fig.update_xaxes(tickformat="%d/%m/%Y", tickangle=25, tickvals=mensajes_por_dia.index, tickmode='array', showline=True, linewidth=2, linecolor='black', range=[inicio_semana, fin_semana])  # Establecer los límites del eje x para la semana actual
        fig.update_yaxes(range=[0, mensajes_por_dia.max()*1.1], fixedrange=True,showline=True, linewidth=2, linecolor='black')  # Fijar el rango del eje y para que siempre sea positivo
        fig.update_traces(marker_color='#6F698C', selector=dict(type='bar'))  # Cambiar el color de las barras
        plot_div = opy.plot(fig, auto_open=False, output_type='div')
        ##############
      
        # Crear un DataFrame vacío
        dfCal = pd.DataFrame()
        calificaciones_cursor = db_connection.db.Calificacion.find()
        dfCal['calificacion'] = [1,2,3,4,5]
        dfCal['contador'] = [0,0,0,0,0]
        for calificacion in calificaciones_cursor:
            dfCal.at[(calificacion['calificacion']-1),'contador'] += 1

        # Colores personalizados
        colores_personalizados = ['#DC3545', '#FFC107', '#007BFF', '#17A2B8', '#28A745']

        # Se crea el gráfico de dona
        plt.figure(figsize=(4, 5))
        plt.pie(dfCal['contador'], startangle=90, colors=colores_personalizados, wedgeprops=dict(width=0.4))

        plt.axis('equal')  # Hace que el gráfico sea circular
        plt.title('Distribución de Calificaciones')
        plt.legend(loc='lower center', labels=['1', '2', '3', '4', '5'], bbox_to_anchor=(0.5, -0.15), ncol=5)
        #plt.axis('equal')  # Hace que el gráfico sea circular
        #######
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot = base64.b64encode(img.read()).decode()
        
        
        #Promedio de calificacion 
        promCalificacion= ((dfCal['contador']*dfCal['calificacion']).sum()) / dfCal['contador'].sum()

        promCalificacion = round(promCalificacion,2)


        ##############
        mensajes_enviados = df['mensaje'].count()
        elementos_mas_repetidos = df['mensaje'].value_counts().head(1).index.tolist()

        ##############
        usuario_dict = db_connection.db.Usuario.find_one({'_id': usuario_id})
            # Crear una instancia del modelo Usuario con los datos obtenidos
        conversaciones = usuario_dict.get('conversaciones', [])
        total_preguntas = sum(len(sublista) for sublista in conversaciones)
        total_conversaciones = len(conversaciones)
      
        return render(request, "pantalla_estadisticas/pantalla_estadisticas.html", {"plot": plot, "usuario_id": usuario_id, "cantidad_usuarios": cantidad_usuarios, "mensajes_enviados": mensajes_enviados, "elementos_mas_repetidos": elementos_mas_repetidos, "promCalificacion": promCalificacion, "plot_div": plot_div,"total_preguntas": total_preguntas,"total_conversaciones":total_conversaciones })

    except Exception as e:
        print(e)
        return render(request, "pantalla_estadisticas/pantalla_estadisticas.html", {"usuario_id": usuario_id})

"""
////////////////////////////////////////////////////////
////// Funciones enfocadas en los comentarios  /////////
////////////////////////////////////////////////////////
"""
@login_required
def pantalla_foro(request,usuario_id,ordenar="mas likes"):
    usuario_id = str(request.session['id_user'])
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

    try:         
        
        # Crear el objeto Paginator
        items_por_pagina = 100
        paginator = Paginator(get_comentariosVer(comentarios,db_connection), items_por_pagina)
        # Obtener el número de página a mostrar
        numero_pagina = request.GET.get('page')
        page_obj = paginator.get_page(numero_pagina)

        usuario_id_Object = ObjectId(str(usuario_id))
        return render(request, "pantalla_foro/pantalla_foro.html", {"usuario_id": usuario_id, "comentarios": page_obj,'ordenar': ordenar,"usuario_id_Object":usuario_id_Object})
    except Exception as e:
        return HttpResponseBadRequest(f"Usuario no válido: {usuario_id}<br> ordenar: {ordenar}<br> comentarios: {comentarios }<br> error: {e}   ")

@login_required
def agregar_replica(request, usuario_id, comentario_id):
    usuario_id = ObjectId(str(request.session['id_user']))
    if request.method == 'POST':
        replica_comentario = request.POST['replica']
        if len(replica_comentario) > 0:

            comentario = db_connection.db.Comentarios.find_one(
                {'_id': ObjectId(comentario_id)})
            
            if comentario:
                replicas = comentario.get('replicas', [])
                replica_dict = {
                    'idReplica':str(ObjectId()),
                    'idRedactorReplica': usuario_id,
                    'contenidoReplica': replica_comentario,
                    'fechaPublicacion': datetime.now(),
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
    usuario_id = ObjectId(str(request.session['id_user']))
    if request.method == 'POST':
        # Obtener el comentario de la base de datos
        comentario = db_connection.db.Comentarios.find_one({'_id': ObjectId(comentario_id)})
        if comentario:
            replicas = comentario.get('replicas', [])
            replicaRevisar = replicas[pos]
            likesActuales = replicaRevisar.get('likes', [])
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
    usuario_id = ObjectId(str(request.session['id_user']))
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
            db_connection.db.Comentarios.update_one({'_id': ObjectId(comentario_id)}, {'$set': {'likes': likes}})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def calificarApp(request, usuario_id):
    usuario_id = ObjectId(str(request.session['id_user']))
    if request.method == 'POST':
        calificacion = request.POST.get('rating')
        # Obtener el comentario de la base de datos
        calificacionEntrante = db_connection.db.Calificacion.find_one({'id_usuario': usuario_id})
        
        if calificacionEntrante:
            idCalificacion = calificacionEntrante.get('_id')
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
    usuario_id = ObjectId(str(request.session['id_user']))
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
def editar_replica(request, usuario_id, comentario_id, idReplica=""):
    if request.method == 'POST':
        nueva_replica = request.POST['replica']
        print(usuario_id, comentario_id, idReplica)
        print(nueva_replica)
        # Actualizar el comentario en la base de datos
        
        db_connection.db.Comentarios.update_one(
            {'_id': ObjectId(comentario_id), 'replicas.idReplica': idReplica},
            {'$set': {'replicas.$.contenidoReplica': nueva_replica}}
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

@login_required
def borrar_replica(request, usuario_id, comentario_id,pos):
    
    if request.method == 'POST':
        # Eliminar el comentario de la base de datos
       
        comentario = db_connection.db.Comentarios.find_one({'_id': ObjectId(comentario_id)})
        comentario['replicas'].pop(pos-1)
        db_connection.db.Comentarios.update_one(
            {'_id': ObjectId(comentario_id)},
            {'$set': {'replicas': comentario['replicas']}}
        )
                 
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
        logout_view(request)

        if form.is_valid():
            correo = form.cleaned_data['correo']
            clave = form.cleaned_data['clave']
            credenciales = db_connection.db.Credenciales
            CorreoExiste = credenciales.find_one({'correo': correo})
            
            if CorreoExiste:
                
                if decifrarClaves(CorreoExiste['clave']) == clave:
                    user_id = str(CorreoExiste['_id'])
                    nombre = db_connection.db.Usuario.find_one({'_id': ObjectId(user_id)})
                    
                    request.session['nombre'] = nombre['nombre']
                    request.session['id_user'] = user_id
                    

                    return redirect('pantalla_menu_inicial/pantalla_menu_inicial.html',usuario_id=user_id)  
                else:
                   
                    messages.error(request, 'Credenciales inválidas') 
            else:
                messages.error(request, 'Credenciales inválidas')


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
        try:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            # Si la fecha no se puede convertir o es None, se establece la fecha actual
            fecha_nacimiento = datetime.now()

        existeCorreo = db_connection.db.Credenciales.find_one({'correo': correo})
        if existeCorreo is None:
            try:
                image = request.FILES['imagen_perfil']
                val = subir_imagen(image.name, image.file)
                if val.status_code == 200:
                    json_img = val.json()
                    url_imagen_perfil = str(json_img['data']['link'])
                    code_delete_img = json_img['data']['deletehash']
                else:
                    url_imagen_perfil = "https://i.imgur.com/0RW7b5J.jpg"
                    code_delete_img = ""
            except Exception as e:
                url_imagen_perfil = "https://i.imgur.com/0RW7b5J.jpg"
                code_delete_img = ""

            usuario = Usuario(nombre=nombre, apellido=apellido, correo=correo, genero=genero, fecha_nacimiento=fecha_nacimiento, url_imagen_perfil=url_imagen_perfil, code_delete_img=code_delete_img, conversaciones=[])
            credenciales = Credenciales(correo=correo, clave=clave)

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
            cifrarClave = cifrarClaves(credenciales.clave)
            usuario_cred = {
                '_id': str(result.inserted_id),
                'correo': credenciales.correo,
                'clave': cifrarClave,
            }

            db_connection.db.Credenciales.insert_one(usuario_cred)
            #enviar_correo_inicio_sesion(correo,  usuario.nombre + ' ' + usuario.apellido)
            return render(request,"pantalla_inicial/pantalla_incial.html")
        else:
            error_message = "Correo ya existe"
            context = {'error_message': error_message}
            return render(request, 'pantalla_registro/pantalla_registro.html', context)
    else:
        return render(request, 'pantalla_registro/pantalla_registro.html')
    
@login_required
def pantalla_perfil_usuario(request, usuario_id):
    usuario_id = ObjectId(str(request.session['id_user']))

    try:
        # Intentar convertir usuario_id a ObjectId
        usuario_object_id = ObjectId(str(request.session['id_user']))
        
        # Realizar la búsqueda en la base de datos usando el ObjectId
        usuario_dict = db_connection.db.Usuario.find_one({'_id': usuario_object_id})
        
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
            
            comentarios = db_connection.db.Comentarios.find({'id_reda_Comet': str(usuario_id)})

          
            # Crear el objeto Paginator
            items_por_pagina = 10
            paginator = Paginator(get_comentariosVer(comentarios, db_connection), items_por_pagina)
            
            # Obtener el número de página a mostrar
            numero_pagina = request.GET.get('page')
            page_obj = paginator.get_page(numero_pagina)
            
            return render(request, 'pantalla_perfil_usuario/pantalla_perfil_usuario.html', {'usuario_id': usuario_id,'usuario_obj':usuario_obj, "comentarios": page_obj})
        else:
            return HttpResponseBadRequest("Usuario no encontrado")
    
    except errors.InvalidId:
        # Manejar el error si el ObjectId no es válido
        return HttpResponseBadRequest(f"Usuario no válido: {usuario_id} - Tipo: {type(usuario_id)}\nError: {str(errors.InvalidId)}\n cuenta_ {str(request.session['id_user'])}")

@login_required    
def editar_usuario(request, usuario_id):
    usuario_id = ObjectId(str(request.session['id_user']))
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
    usuario_id =str(request.session['id_user'])
    palabraBuscar = request.GET.get('palabraBuscar')
    
    if request.method == 'GET':
        if palabraBuscar != None and palabraBuscar != "":
            comentarios = db_connection.db.Comentarios.find({ 'comentario': { '$regex': str(palabraBuscar), '$options': 'i' } })
        else:
            comentarios = db_connection.db.Comentarios.find()
    items_por_pagina = 50
    
    # Obtener el número de página a mostrar
    
   
    paginator = Paginator(get_comentariosVer(comentarios,db_connection), items_por_pagina)
    try: 
        numero_pagina = request.GET.get('page')
        page_obj = paginator.get_page(numero_pagina)
        usuario_dict = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})
        url_imagen_perfil = usuario_dict['url_imagen_perfil']
        nombre_usuario = usuario_dict['nombre'] + " " + usuario_dict['apellido']
        conversaciones = usuario_dict['conversaciones']
        usuario_id_Object = ObjectId(str(usuario_id))

        # Crear el objeto Paginator
        
       
        if len(conversaciones) == 0:
            conversaciones.append([])
            posicion = 0
            conversacion = conversaciones[posicion]
            db_connection.db.Usuario.update_one({'_id': ObjectId(usuario_id)}, {'$set': {'conversaciones': conversaciones}})

        else:
            posicion = posicion
            conversacion = conversaciones[posicion]
        return render(request, "pantalla_chatbot/pantalla_chatbot.html", {"usuario_id": usuario_id,"url_imagen_perfil":url_imagen_perfil,'nombre_usuario': url_imagen_perfil,"conversaciones": conversaciones,"conversacion":conversacion,"posicion":posicion, "comentarios": page_obj,"usuario_id_Object":usuario_id_Object})
    except :
        # Manejar el error si el ObjectId no es válido
        #return render(request,"pantalla_chatbot/pantalla_chatbot.html")
        return HttpResponseBadRequest(f"Usuario no válido: {usuario_id}<br> posicion: {posicion} <br> palabraBuscar: {palabraBuscar} <br> comentarios: {comentarios}   ")

@login_required
def crearNuevoChat(request, usuario_id,posicion=0):
    usuario_id = ObjectId(str(request.session['id_user']))
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
def vaciarChat(request,usuario_id,posicion):
    usuario_id = ObjectId(str(request.session['id_user']))
    posicion=int(posicion)
    if request.method == 'POST':
        usuario = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})
        if usuario:
            conversaciones = usuario.get('conversaciones', [])
            chat = conversaciones[posicion]
            if len(chat) > 0:
                chat.clear()
                conversaciones[posicion] = chat
                db_connection.db.Usuario.update_one({'_id': ObjectId(usuario_id)}, {'$set': {'conversaciones': conversaciones}})
                return redirect('pantalla_chatbot', usuario_id=usuario_id,posicion=posicion)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def eliminarChat(request,usuario_id,posicion):
    usuario_id = ObjectId(str(request.session['id_user']))
    posicion=int(posicion)
    if request.method == 'POST':
        usuario = db_connection.db.Usuario.find_one({'_id': ObjectId(usuario_id)})
        if usuario:
            conversaciones = usuario.get('conversaciones', [])
            if len(conversaciones) > 1:
                conversaciones.pop(posicion)
                db_connection.db.Usuario.update_one({'_id': ObjectId(usuario_id)}, {'$set': {'conversaciones': conversaciones}})
                lugar = posicion - 1
                if lugar < 0:
                    lugar = 0
                return redirect('pantalla_chatbot', usuario_id=usuario_id,posicion=lugar)
            else:
                vaciarChat(request,usuario_id,posicion)
            
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def enviarMensajeChatBot(request,usuario_id,posicion=0):
    usuario_id = ObjectId(str(request.session['id_user']))

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
                salida = "No entendí tu pregunta"

            else:
                pregunta_inicial = pregunta
                pregunta = pregunta.lower()
                pregunta = pregunta.replace("  ", "")
                pregunta = eliminar_tildes(pregunta)
                
                try:
                    

                    salida = comunicacionMillyApi(pregunta)
                                  
                except:
                    salida = "No entendí tu pregunta"
                    
                nuevo_mensaje ={
                    'pregunta': pregunta_inicial,
                    'respuesta': salida,
                    'fecha' : datetime.now()
                }
                
                conversacion.append(nuevo_mensaje)
                db_connection.db.Usuario.update_one({'_id': ObjectId(usuario_id)}, {'$set': {'conversaciones': conversaciones}})
                mensaje_dict = {                 
                    'mensaje' : pregunta,
                    'fecha' : datetime.now()
                }
                
                db_connection.db.Mensajes.insert_one(mensaje_dict)
        return redirect('pantalla_chatbot', usuario_id=usuario_id,posicion=posicion)

