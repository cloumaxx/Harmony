import json
from django.http import JsonResponse
from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
import requests
import json

from millyApp.rasaBot.y.actions.actions import traducir



def send_to_rasa(message):
    message = message.lower()
    message = traducir(message)
    print("Enviando mensaje a Rasa:   ",message.lower())
    rasa_url = 'http://localhost:5005/webhooks/rest/webhook'
    payload = {
        'sender': 'user_id',
        'message': message
    }
    response = requests.post(rasa_url, json=payload)
    return response.json()


