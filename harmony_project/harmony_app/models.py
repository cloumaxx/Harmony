from django.db import models

# Create your models here.
class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField()
    clave = models.CharField(max_length=10)
    edad = models.DecimalField(max_digits=2,decimal_places=0)

    class Meta:
        db_table = 'usuarioDB'

    def __str__(self):
        return f"Usuario ID: {self.id}, Nombre: {self.nombre}, Apellido: {self.apellido}"
