from django.db import models
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1)
    url_imagen_perfil = models.CharField(max_length=300)
    code_delete_img = models.CharField(max_length=300)
    conversaciones = ArrayField(models.JSONField())

    class Meta:
        db_table = 'usuarioDB'
    
    def getNombreCompleto(self):
        return f"{self.nombre} {self.apellido}"
    
    def __str__(self):
        return f"Usuario ID: {self.id}, Nombre: {self.nombre}, Apellido: {self.apellido}, Correo: {self.correo},Genero: {self.genero}, Fecha de nacimiento: {self.fecha_nacimiento}, "

class Calificacion(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario = models.CharField(max_length=100)
    calificacion = models.IntegerField()
    fecha = models.DateField()

    class Meta:
        db_table = 'calificacionDB'
    
    def __str__(self):
        return f"Calificacion ID: {self.id}, ID del usuario: {self.id_usuario}, Calificacion: {self.Calificacion}, Fecha: {self.fecha}"
class Credenciales(models.Model):
    id = models.AutoField(primary_key=True)
    correo = models.EmailField(max_length=100)
    clave = models.CharField(max_length=10)

    class Meta:
         db_table = 'credencialesDB'

    def __str__(self):
        return f"Credenciales ID: {self.id}, Correo: {self.correo}, Clave: {self.clave}"
    
class Comentarios(models.Model):
    id = models.AutoField(primary_key=True)
    id_reda_Comet = models.CharField(max_length=100) 
    comentario = models.CharField(max_length=500)
    likes = ArrayField(models.CharField(max_length=100)) 
    fechaPublicacion = models.DateField()
    replicas = ArrayField(models.JSONField()) 

    class Meta:
        db_table = 'comentariosDB'
    
    def __str__(self):
        return f"Comentarios ID: {self.id}, ID del redactor: {self.id_reda_Comet}, Comentario: {self.comentario}, Likes: {self.likes}, Fecha de publicacion: {self.fechaPublicacion}"
    
class Replicas(models.Model): 

    idRedactorReplica = models.CharField(max_length=100)
    contenidoReplica  =models.CharField(max_length=600)
    likes = ArrayField(models.CharField(max_length=100)) 
    fechaPublicacion = models.DateField()
    
    def __str__(self):
        return f" ID del redactor: {self.idRedactorReplica}, Contenido de la replica: {self.contenidoReplica}, Likes: {self.likes}"


class Mensajes(models.Model):
    id = models.AutoField(primary_key=True)
    mensaje = models.CharField(max_length=1000)
    fecha = models.DateField()

    class Meta:
        db_table = 'mensajesDB'

    def __str__(self):
        return f"Mensaje ID: {self.id}, Mensaje: {self.mensaje}, Fecha: {self.fecha}"