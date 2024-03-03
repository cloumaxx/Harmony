from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from harmonyProject.database import MongoDBConnection
from harmonyApp.models import Credenciales, Usuario
from harmonyApp.views import pantalla_registro
from harmonyApp.operations.utils import comunicacionMillyApi

class PantallaRegistroTestCase(TestCase):
    db_connection = MongoDBConnection()

    def setUp(self):
        # Configuración inicial para las pruebas
        self.factory = RequestFactory()
        #self.user = User.objects.create_user(username='testuser', email='samymartsa@yahoo.com', password='aaaa')

    def test_pantalla_registro(self):
        # Crear una solicitud POST para la vista con datos de formulario simulados
        data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'correo': 'samymartsa@yahoo.com',
            'clave': 'testpassword',
            'genero': 'M',
            'fecha_nacimiento': '1990-01-01',  # Formato: Año-Mes-Día
        }
        existeCorreo = self.db_connection.db.Credenciales.find_one({'correo': data['correo']})
        self.assertTrue(existeCorreo)

        # Verificar la respuesta y el comportamiento esperado
        #self.assertEqual(response.status_code, 302)  # Comprobar redireccionamiento


        # Verificar que se envió el correo de confirmación (puedes simular esto utilizando mocks)


class TestComunicacionMillyApi(TestCase):
    def test_comunicacion_milly_api_success(self):
        
        respuesta = comunicacionMillyApi('cual es tu nombre')
        self.assertNotEqual(respuesta, 'No entendi tu pregunta')

"""
    def test_comunicacion_milly_api_failure(self):
        # Configurar el mock para simular una respuesta fallida de la API
        
        # Llamar a la función con una pregunta
        respuesta = comunicacionMillyApi('Hola, ¿cómo estás?')

        # Verificar que la función devuelva el mensaje de error
        self.assertEqual(respuesta, 'No entendí tu pregunta')"""