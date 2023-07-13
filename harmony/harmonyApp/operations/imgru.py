import requests

def subir_imagen(nombre,ruta):
    url = "https://api.imgur.com/3/image"

    payload = {'album': 'kc9xKmo'}
    files=[
        ('image', (nombre, ruta, 'image/jpeg'))
    ]
    headers = {
    'Authorization': 'Bearer c32f1c36a7546cd48e992a4f1e66c01dfbfdecdc',
    'Cookie': 'IMGURSESSION=ff9914be1a9ec8a81b1145e21da8dadc; _nc=1'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    return response
