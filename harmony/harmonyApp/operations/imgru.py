import requests

cod_athorization = "Bearer c32f1c36a7546cd48e992a4f1e66c01dfbfdecdc"
code_cookie = "IMGURSESSION=ff9914be1a9ec8a81b1145e21da8dadc; _nc=1"

def subir_imagen(nombre,ruta):
    url = "https://api.imgur.com/3/image"

    payload = {'album': 'kc9xKmo'}
    files=[
        ('image', (nombre, ruta, 'image/jpeg'))
    ]
    headers = {
    'Authorization': cod_athorization,
    'Cookie': code_cookie
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return response

def eliminar_imagen(code):
    url = "https://api.imgur.com/3/image/"+code

    payload = {}
    files={}
    headers = {
    'Authorization': 'Client-ID 7dd8521baa79ea0',
    'Cookie': 'IMGURSESSION=793735e10fc5d27fee5104344e9744e3; _nc=1'
    }

    response = requests.request("DELETE", url, headers=headers, data=payload, files=files)

    return response

def actualizar_imagen(code,nombre,ruta):
    respuesta_subida = subir_imagen(nombre,ruta)
    respuesta_eliminacion = eliminar_imagen(code)
    if respuesta_subida.status_code == 200 and respuesta_eliminacion.status_code == 200:
        return respuesta_subida
    elif respuesta_subida.status_code == 200 and respuesta_eliminacion.status_code != 200:
            return respuesta_eliminacion
    else:
            return respuesta_eliminacion