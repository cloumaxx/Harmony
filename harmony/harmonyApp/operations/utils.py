
from bson import ObjectId


from django.conf import settings


def get_Nombre(comentario,db_connection):
    
    user = db_connection.db.Usuario.find_one({'_id': ObjectId(comentario['id_reda_Comet'])})
    try:
        return user['nombre']
    except user.DoesNotExist:
        return None
    
def get_inforeplicas(idReplica,db_connection):
    replicas = db_connection.db.Replicas.find_one({'_id': ObjectId(idReplica)})
    try:

        nombreRedactor = db_connection.db.Usuario.find_one(
            {'_id': ObjectId(replicas['idRedactorReplica'])})['nombre']
        dic = {
            "idReplica":str(idReplica),
            "idRedactorReplica": replicas['idRedactorReplica'],
            "nombreRedactor": nombreRedactor,
            "contenidoReplica": replicas['contenidoReplica'],
            "likes": replicas['likes']
        }
        return dic
    except:
        return None
