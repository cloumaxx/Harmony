from django.db import models

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