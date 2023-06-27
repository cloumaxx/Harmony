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


    class Meta:
        db_table = 'usuarioDB'
    
    def getNombreCompleto(self):
        return f"{self.nombre} {self.apellido}"
    
    def __str__(self):
        return f"Usuario ID: {self.id}, Nombre: {self.nombre}, Apellido: {self.apellido}, Correo: {self.correo},Genero: {self.genero}, Fecha de nacimiento: {self.fecha_nacimiento}, "

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
    id_replicas = ArrayField(models.CharField(max_length=100)) 



    class Meta:
        db_table = 'comentariosDB'
    
    def __str__(self):
        return f"Comentarios ID: {self.id}, ID del redactor: {self.id_reda_Comet}, Comentario: {self.comentario}, Likes: {self.likes}, ID de replicas: {self.id_replicas}"
    
class Replicas(models.Model): 
    id = models.AutoField(primary_key=True) 
    idComentario = models.CharField(max_length=100)    
    idRedactorReplica = models.CharField(max_length=100)
    contenidoReplica  =models.CharField(max_length=600)
    likes = ArrayField(models.CharField(max_length=100)) 
    
    class Meta:
        db_table = 'replicasDB'
    
    def __str__(self):
        return f"Replicas ID: {self.id}, ID del comentario: {self.idComentario}, ID del redactor: {self.idRedactorReplica}, Contenido de la replica: {self.contenidoReplica}, Likes: {self.likes}"