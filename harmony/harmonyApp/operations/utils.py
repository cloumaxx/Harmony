
from email.mime.image import MIMEImage
import json
from bson import ObjectId
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
import spacy
import unicodedata
import string

import requests

from harmonyProject.settings import KEY_Contraseñas

def get_Nombre(comentario, db_connection):
    try:
        user = db_connection.db.Usuario.find_one({'_id': ObjectId(comentario['id_reda_Comet'])})
        return user['nombre']
    except Exception:
        return None

def get_img_perfil(comentario, db_connection):  
    try:
        user = db_connection.db.Usuario.find_one(
        {'_id': ObjectId(comentario['id_reda_Comet'])})
        return user['url_imagen_perfil']
    except Exception:
        return None

def get_comentariosVer(comentarios,db_connection):
    
    comentarios_con_nombre_id = [(comentario, get_Nombre(comentario,db_connection), get_img_perfil(comentario,db_connection),str(
            comentario['_id'])) for comentario in comentarios]
    try:    
        for comentario in comentarios_con_nombre_id:
            comentario2 = comentario[0]
            replicasComentario=comentario[0]['replicas']
        
            if len(replicasComentario)>0:
                new_id_replicas = []
                for replica in replicasComentario:
                    
                    new_id_replicas.append(get_inforeplicas(replica,db_connection))
                    
                comentario2['replicas'] = new_id_replicas
        return comentarios_con_nombre_id
    except Exception as e:
        return None

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
            "idReplica": replica.get('idReplica', "") if replica.get('idReplica') else "1",
            "likes": replica['likes']
        }
        return dic
    except:
        return None

def eliminar_tildes(texto):
    return ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))
def eliminar_puntuacion(texto):
    # Crea una tabla de traducción que mapea cada signo de puntuación a None
    tabla = {ord(caracter): None for caracter in string.punctuation + '¿¡'}
    return texto.translate(tabla)
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
        <title>Correo de Registro</title>
    </head>
    <body>
        <p>Hola, <b>{nombre}</b>.</p>
        <p>Has iniciado sesión exitosamente en HarmonyApp.</p>
    </body>
    </html>
    """
    
    # Adjunta el mensaje HTML al correo
    msg.attach(MIMEText(mensaje_html, 'html'))

    # Inicia una conexión SMTP segura y envía el correo
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(remitente, contraseña)
            server.send_message(msg)
        return "Correo electrónico enviado con éxito."
    except Exception as e:
        return "Error al enviar el correo electrónico: " + str(e)
  
def detectarStopWords(texto_a_analizar):
    # Carga el modelo de spaCy para español
    nlp = spacy.load('es_core_news_sm')

    # Texto de ejemplo

    # Procesa el texto
    doc = nlp(texto_a_analizar)

    # Filtra las stop words
    palabras_filtradas = [token.text for token in doc if not token.is_stop]
    print("-->",palabras_filtradas)
    return palabras_filtradas

def cifrarClaves(clave):
    cipher = Fernet(KEY_Contraseñas)
    texto_cifrado = cipher.encrypt(clave.encode())
    return texto_cifrado

def decifrarClaves(clave):
    cipher = Fernet(KEY_Contraseñas)
    texto_descifrado = cipher.decrypt(clave).decode()
    return texto_descifrado

def comunicacionMillyApi(pregunta ):
    webhook_url = 'https://rasaharmony.azurewebsites.net/webhooks/rest/webhook'

    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "sender": "user1",
        "message": pregunta
    }
    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        return response_data[0]['text']
    else:
        response_data = response.json()

        return 'No entendi tu pregunta'
