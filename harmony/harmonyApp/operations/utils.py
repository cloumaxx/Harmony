
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

def get_comentariosVer(comentarios,db_connection):
    comentarios_con_nombre_id = [(comentario, get_Nombre(comentario,db_connection), get_img_perfil(comentario,db_connection),str(
        comentario['_id'])) for comentario in comentarios]
    
    for comentario_tuple in comentarios_con_nombre_id:
        comentario2 = comentario_tuple[0]
        replicasComentario=comentario_tuple[0]['replicas']
        
        if len(replicasComentario)>0:
            new_id_replicas = []
            for replica in replicasComentario:
                new_id_replicas.append(get_inforeplicas(replica,db_connection))
            comentario2['id_replicas'] = new_id_replicas  
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
            "likes": replica['likes']
        }
        return dic
    except:
        return None
