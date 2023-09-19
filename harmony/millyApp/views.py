import json
from django.http import JsonResponse
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import requests
import json
from millyApp.rasaBot.y.actions.actions import detectarStopWords

from millyApp.rasaBot.y.actions.actions import  traducirAEspañol, traducirMensajeSalida



def send_to_rasa(message):
    try:
        message = message.lower()      
        messageEspañol = traducirAEspañol(message)
        validarStopWords = detectarStopWords(messageEspañol.text)
        print(validarStopWords)
        if len(validarStopWords) > 0:
            idioma = messageEspañol.src
            messageEspañol = messageEspañol.text
            rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
            payload = {
                'sender': 'user_id',
                'message': messageEspañol
            }
            response = requests.post(rasa_url, json=payload)
    
            response = response.json()
            if idioma != 'es':
                traducir = traducirMensajeSalida(response[0]['text'],'es',idioma)
                response[0]['text'] = traducir
        else:
            response = [{'text':'No entiendo lo que me dices'}]
    except Exception as error :
        print("Error al traducir:   ", error    )
    
          
    return response


