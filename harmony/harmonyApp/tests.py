import random
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from harmonyProject.database import MongoDBConnection
from harmonyApp.models import Credenciales
from harmonyApp.views import pantalla_registro
from harmonyApp.operations.utils import cifrarClaves, comunicacionMillyApi, decifrarClaves

class PantallaRegistroTestCase(TestCase):
    db_connection = MongoDBConnection()

    def test_pantalla_registro(self):
        # Crear una solicitud POST para la vista con datos de formulario simulados
        data = {
            'nombre': 'John',
            'apellido': 'Doe',
            'correo': 'prueba'+str(random.randint(0, 150))+'@yahoo.com',
            'clave': 'testpassword',
            'genero': 'M',
            'fecha_nacimiento': '1990-01-01',  
            "url_imagen_perfil": "https://i.imgur.com/0RW7b5J.jpg",
            "code_delete_img": "",
            "conversaciones": []
        }
        
    
        # Simular la existencia del correo en la base de datos antes de realizar la solicitud
        existeCorreo = self.db_connection.db.Credenciales.find_one({'correo': data['correo']})
        self.assertFalse(existeCorreo)  # El correo no debe existir antes de la solicitud
        
        # Realizar la solicitud a la vista de registro
        response = self.client.post(reverse('pantalla_registro'), data)
        
        # Verificar que la solicitud fue exitosa (código de estado 200)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se haya creado una credencial para el usuario
        existeCorreoDespues = self.db_connection.db.Credenciales.find_one({'correo': data['correo']})
        self.assertTrue(existeCorreoDespues)  # El correo debe existir después de la solicitud

    def test_validar_cifrado(self):
        """
        Verifica que la contraseña sea cifrada correctamente
        """
        # Configuración inicial para las pruebas
        clave = 'testpassword'

        clave_cifrada = cifrarClaves(clave)
        clave_descifrada = decifrarClaves(clave_cifrada)

        self.assertEquals(clave, clave_descifrada)

class TestComunicacionMillyApi(TestCase):
    def test_comunicacion_milly_api_success(self):
        # Probar comunicación exitosa con la API
        respuesta = comunicacionMillyApi('cual es tu nombre')
        self.assertNotEqual(respuesta, 'No entendí tu pregunta')

    """def test_comunicacion_milly_api_failure(self):
        # Probar comunicación fallida con la API
        respuesta = comunicacionMillyApi('')
        self.assertEqual(respuesta, 'No entendí tu pregunta')
    """