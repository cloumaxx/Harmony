
from bson import ObjectId


from django.conf import settings


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


def get_inforeplicas(idReplica, db_connection):
    
    replicas = db_connection.db.Replicas.find_one({'_id': ObjectId(idReplica)})
    try:
        usuario= db_connection.db.Usuario.find_one(
            {'_id': ObjectId(replicas['idRedactorReplica'])})
        nombreRedactor = usuario['nombre']
        url_imagen_perfil = usuario['url_imagen_perfil']
        dic = {
            "idReplica": str(idReplica),
            "nombreRedactor": nombreRedactor,
            "url_imagen_perfil": url_imagen_perfil,
            "contenidoReplica": replicas['contenidoReplica'],
            "likes": replicas['likes']
        }
        return dic
    except:
        return None
