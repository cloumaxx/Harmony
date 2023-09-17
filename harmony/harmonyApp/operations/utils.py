
from email.mime.image import MIMEImage
from bson import ObjectId


from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

def get_Nombre(comentario, db_connection):

    user = db_connection.db.Usuario.find_one(
        {'_id': ObjectId(comentario['id_reda_Comet'])})
    try:
        return user['nombre']
    except user.DoesNotExist:
        return None


def get_img_perfil(comentario, db_connection):
   
    user = db_connection.db.Usuario.find_one(
        {'_id': ObjectId(comentario['id_reda_Comet'])})
    try:
        
        return user['url_imagen_perfil']
    except user.DoesNotExist:
        return None

def get_comentariosVer(comentarios,db_connection):
    comentarios_con_nombre_id = [(comentario, get_Nombre(comentario,db_connection), get_img_perfil(comentario,db_connection),str(
        comentario['_id'])) for comentario in comentarios]
    
    for comentario in comentarios_con_nombre_id:
        comentario2 = comentario[0]
        replicasComentario=comentario[0]['replicas']
       
        if len(replicasComentario)>0:
            new_id_replicas = []
            for replica in replicasComentario:
                
                new_id_replicas.append(get_inforeplicas(replica,db_connection))
                
            comentario2['replicas'] = new_id_replicas
    return comentarios_con_nombre_id

def get_inforeplicas(replica, db_connection):    
    try:
        usuario= db_connection.db.Usuario.find_one(
            {'_id': ObjectId(replica['idRedactorReplica'])})
        nombreRedactor = usuario['nombre']
        url_imagen_perfil = usuario['url_imagen_perfil']
        dic = {
            "idRedactorReplica": replica['idRedactorReplica'],
            "nombreRedactor": nombreRedactor,
            "url_imagen_perfil": url_imagen_perfil,
            "contenidoReplica": replica['contenidoReplica'],
            "fechaPublicacion":replica['fechaPublicacion'],
            "likes": replica['likes']
        }
        return dic
    except:
        return None

def enviar_correo_inicio_sesion(destinatario, nombre):
    # Configura los parámetros del servidor SMTP de Outlook
    smtp_server = 'smtp.office365.com'
    smtp_port = 587  # Puerto SMTP para TLS

    # Tu dirección de correo electrónico de Outlook y contraseña
    remitente = 'tesis_harmony2023@hotmail.com'
    contraseña = '2023_harmony_necesito_graduarme'

    # Crea el objeto MIMEMultipart para el correo
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = "Registro exitoso en Harmony"

    # Crea el cuerpo del mensaje en formato HTML
    mensaje_html = f"""
    <html>

    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://getbootstrap.com/docs/5.3/assets/css/docs.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    </head>

    <body>
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <img src="cid:imagen">

                </div>
                <div class="col-md-8">
                    <p>Hola, <b>{nombre}</b>.</p>
                    <p>Has iniciado sesión exitosamente en HarmonyApp.</p>
                </div>
            </div>

        </div>

    </body>

    </html>
    """
    
    # Adjunta el mensaje HTML al correo
    msg.attach(MIMEText(mensaje_html, 'html'))

    # Descarga la imagen desde la URL
    imagen_url = 'https://i.imgur.com/x3plOXF.png'
    imagen_respuesta = requests.get(imagen_url)
    imagen_data = imagen_respuesta.content

    # Adjunta la imagen al correo y asigna un CID para referenciarla en el HTML
    imagen_adjunta = MIMEImage(imagen_data)
    imagen_adjunta.add_header('Content-Disposition', 'attachment; filename="imagen.png"')
    imagen_adjunta.add_header('Content-ID', '<imagen>')
    msg.attach(imagen_adjunta)

    # Inicia una conexión SMTP segura y envía el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(remitente, contraseña)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return "Correo electrónico enviado con éxito."
    except Exception as e:
        return "Error al enviar el correo electrónico: " + str(e)
    
